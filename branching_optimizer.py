import numpy as np
from scipy.linalg import expm, inv, logm, det
from scipy.optimize import minimize, Bounds
from scipy.integrate import quad
import model
import dynamic

class ThreeType(model.Model):
    def __init__(self, params, start):

        p = 3
        pops = []
        for i in range(p):
            pop = model.Population(start[i], label = 'pop ' + str(i))
            pops.append(pop)

        events = []
        for i, pop in enumerate(pops):
            events.append(model.SimpleBirth(pops[i], params[i]))
            events.append(model.SimpleDeath(pops[i], params[i] - params[i + p]))
            for j, pop2 in enumerate(pops):
                amount = j
                if i == j:
                    continue;
                elif j > i:
                    amount -= 1
                events.append(model.SimpleTransfer(pop, pop2, params[2 * p + i * (p - 1) + amount]))

        self = super().__init__(pops, events, name = 'Three Type')

class PS(model.Model):
    def __init__(self, params, start):

        p0 = model.Population(start[0], label = 'pop 0')
        p1 = model.Population(start[1], label = 'pop 1')
        pops = [p0, p1]

        events = []
        events.append(model.SimpleBirth(p0, params[0]))
        events.append(model.SimpleBirth(p1, params[1]))
        events.append(model.SimpleDeath(p0, params[0] - params[2]))
        events.append(model.SimpleDeath(p1, params[1] - params[3]))
        events.append(model.SimpleTransfer(p0, p1, params[4]))
        events.append(model.SimpleTransfer(p1, p0, params[5]))



        self = super().__init__(pops, events, name = 'Phenotypic Switch')

class OT(model.Model):
    def __init__(self, params, start):
        p0 = model.Population(start[0], label = 'pop 0')
        pops = [p0]
        events = []
        events.append(model.SimpleBirth(p0, params[0]))
        events.append(model.SimpleDeath(p0, params[0] - params[1]))
        self = super().__init__(pops, events, name = 'Phenotypic Switch')

def meanMat(evolutionMat, t):
    return expm(evolutionMat * t)

def elementarySigma(birthrates, evolutionMat, j, t):

    p = len(evolutionMat)

    def m(t):
        return expm(evolutionMat * t)

    def mj(t):
        return m(t)[j]

    def integrand(t, k, l):
        def f(tau):
            res = (m(t - tau).T @ np.diag(birthrates * mj(tau)) @ m(t - tau))[k][l]
            return res
        return f

    def integral(t):
        mat = []
        for k in range(p):
            row = []
            for l in range(p):
                val, err = quad(integrand(t, k, l), 0, t)
                row.append(val)
            mat.append(row)
        return np.array(mat)

    res = 2 * integral(t) + np.diag(mj(t)) - np.array([mj(t)]).T @ np.array([mj(t)])
    return res

def tdnll(actual, expected, logDetSigma, invSigma):
    drift = np.array([actual - expected])
    return logDetSigma + (drift @ invSigma @ drift.T)[0][0]

def get_likelihood(params, starts, times, reps, data):

    # get info from parameters
    (birthrates, evolutionMat) = convert(params)
    p = len(birthrates)

    #make a list of the mean evolution matrices
    #index: time
    meanMats = []
    for t in times:
        meanMats.append(meanMat(evolutionMat, t))

    #make a list of average results
    #index: initial condition, time
    meansList = []
    for start in starts:
        means = []
        for l, t in enumerate(times):
            means.append(start @ meanMats[l])
        meansList.append(means)

    #make elementary covariance matrices
    #index: population, time
    eSigmasList = []
    for j in range(p):
        sigmas = []
        for t in times:
            next = elementarySigma(birthrates, evolutionMat, j, t)
            sigmas.append(next)
        eSigmasList.append(sigmas)

    #make covariance matrices for our starting conditions
    #indices: initial condition, time
    sigmasList = []
    inverseSigmasList = []
    for start in starts:
        sigmas = []
        invSigmas = []
        for l, t in enumerate(times):
            for j in range(p):
                count = start[j]
                if j == 0:
                    sigma = count * eSigmasList[0][l]
                else:
                    sigma = np.add(sigma, count * eSigmasList[j][l])
            sigmas.append(sigma)
            invSigmas.append(inv(sigma))
        sigmasList.append(sigmas)
        inverseSigmasList.append(invSigmas)


    total = 0
    for i, start in enumerate(starts):
        for l, time in enumerate(times):
            expected = meansList[i][l]

            logDetSigma = np.log(det(sigmasList[i][l]))

            invSigma = inverseSigmasList[i][l]
            for r in range(reps):
                actual = data[i][l][r]
                total += tdnll(actual, expected, logDetSigma, invSigma)

    return total

def optimize(starts, times, reps, data):

    initialEvo = estimate_evolution_mat(starts, times, reps, data)
    initialParams = deconvert_full(initialEvo)


    def f(params):
        l = get_likelihood(params, starts, times, reps, data)
        print(l)
        return l

    res =  minimize(f, initialParams, bounds = Bounds(0.05, 2), method = 'L-BFGS-B')
    return res


#generates test data for a given model.
#outputs a 4D nested array: starts x times x reps x pops

def generate_data(Model, params, starts, times, reps):
    data = []
    for start in starts:
        timeData = []
        for time in times:
            repData = []
            for _ in range(reps):
                model = Model(params, start)

                model.empty_run(time)
                datum = []
                for pop in model.get_populations():
                    datum.append(pop.get_size())
                repData.append(np.array(datum))
            timeData.append(repData)
        data.append(timeData)
    return data

#converts and deconverts parameters into birthrates and evolution matrix

def convert(params):
    p = int(np.floor(len(params) ** 0.5))

    evolutionMat = np.zeros((p, p))
    birthrates = []

    for i, param in enumerate(params):
        if i < p:
            birthrates.append(param)
        elif i < 2 * p:
            r = i - p
            evolutionMat[r][r] = evolutionMat[r][r] + param
        else:
            d = (i - 2 * p) // (p - 1)
            r = (i - 2 * p) % (p - 1)
            if r >= d:
                r += 1
            evolutionMat[d][d] = evolutionMat[d][d] - param
            evolutionMat[d][r] = evolutionMat[d][r] + param

    birthrates = np.array(birthrates)
    return (birthrates, evolutionMat)

def deconvert_part(evolutionMat):
    netGrowths = []
    transfers = []

    for i, row in enumerate(evolutionMat):
        netGrowth = 0
        for j, datum in enumerate(row):
            if i == j:
                netGrowth += datum
            else:
                netGrowth += datum
                transfers.append(datum)
        netGrowths.append(netGrowth)

    return np.concatenate((netGrowths, transfers)).tolist()

def deconvert_full(evolutionMat):
    p = len(evolutionMat)
    laterParams = deconvert_part(evolutionMat)
    firstParams = []
    for i in range(p):
        netGrowth = laterParams[i]
        if netGrowth > 0:
            firstParams.append(2 * netGrowth)
        else:
            firstParams.append(- 1 * netGrowth)
    firstParams.extend(laterParams)
    return firstParams



def estimate_evolution_mat(starts, times, reps, data):
    starts = np.array(starts)


    for i, time in enumerate(times):
        avgRow = []
        for j, start in enumerate(starts):
            for k in range(reps):
                datum = data[j][i][k]
                if k == 0:
                    avg = datum
                else:
                    avg = avg + datum
            avg = avg / reps
            avgRow.append(avg)
        evoAvg = logm(inv(starts.T @ starts) @ starts.T @ np.array(avgRow)) / time
        if i == 0:
            overall = evoAvg
        else:
            overall = overall + evoAvg
    overall = overall / len(times)

    return overall






def full_test():
    times = [1, 2, 3]
    starts = [[1000, 0], [0, 1000], [1000, 1000]]
    reps = 10


    birthrates = [1, 1]
    deathrates = [0.5, 0.5]
    switchingrates = [0.1, 0.1]

    params = birthrates + deathrates + switchingrates
    data = generate_data(params, starts, times, reps)
    goal = get_likelihood(params, starts, times, reps, data)
    print(data)
    print(goal)
    input()
    res = optimize(params, starts, times, reps, data)
    print(res.x)
    print(res.fun)
    print(get_likelihood(params, starts, times, reps, data))

def short_test():

    birthrates = np.array([3, 3])
    evolutionMat = np.array([[1.6, 0.4], [0.4, 1.6]])
    m = elementarySigma(birthrates, evolutionMat, 0, 0.1)
    print(det(m))

def run_tests():

    def test_convert():
        params = [1, 10, 100, 1000, 10000, 100000]
        expected1 = np.array([1, 10])
        expected2 = np.array([[-10099, 10000], [100000, -100990]])
        (actual1, actual2) = convert(params)
        if (actual1 - expected1).any():
            print('expected ' + str(expected1) + ' but got ' + str(actual1))
        elif (actual2 - expected2).any():
            print('expected ' + str(expected2) + ' but got ' + str(actual2))
        else:
            print('passed test 1')

    def test_OT():
        times = [1]
        starts = [[100]]
        reps = 10000
        params = [1, 0.5]

        data = generate_data(OT, params, starts, times, reps)

        goal = get_likelihood(params, starts, times, reps, data)
        print(data)
        print(goal)
        res = optimize(params, starts, times, reps, data)
        print(res.x)
        print(res.fun)
        print(get_likelihood(params, starts, times, reps, data))

    def test_PS():
        times = [1]
        starts = np.array([[1000, 0], [0, 1000]])
        reps = 1000
        params = [1, 1, 0.2, 0.2, 0.1, 0.1]

        data = generate_data(PS, params, starts, times, reps)

        goal = get_likelihood(params, starts, times, reps, data)
        print(data)
        print(goal)
        res = optimize(starts, times, reps, data)
        print(res.x)
        print(res.fun)
        print(get_likelihood(params, starts, times, reps, data))

    def test_gen_and_avg():
        times = [1, 2]
        starts = [[0, 1000]]
        reps = 100
        params = [1, 1, 1, 1, 0.1, 0.1]
        (birthrates, evolutionMat) = convert(params)
        print(birthrates)
        print(evolutionMat)
        data = generate_data(PS, params, starts, times, reps)
        avgs = []
        avgs_actual = []
        for i, start in enumerate(starts):
            row = []
            row_actual = []
            for j, time in enumerate(times):
                for k in range(reps):
                    if k == 0:
                        avg_actual = data[i][j][k]
                    else:
                        avg_actual = avg_actual + data[i][j][k]
                avg_actual = avg_actual / reps
                avg = np.array(start) @ meanMat(evolutionMat, time)
                row.append(avg)
                row_actual.append(avg_actual)
            avgs.append(row)
            avgs_actual.append(row_actual)
        print(avgs)
        print(avgs_actual)

    def test_estimate():
        times = [1]
        starts = np.array([[1000, 0], [0, 1000]])
        reps = 100
        params = [1, 1, 1, 1, 0.1, 0.1]

        data = generate_data(PS, params, starts, times, reps)

        est = estimate_evolution_mat(starts, times, reps, data)
        print(est)

    def test_deconvert():
        params = [1, 1, 0.5, 0.5, 0.1, 0.1]
        (birthrates, evolutionMat) = convert(params)
        print(birthrates)
        print(evolutionMat)
        endingParams = deconvert_full(evolutionMat)
        print(endingParams)





    tests = [test_convert, test_OT, test_PS, test_gen_and_avg, test_estimate, test_deconvert]
    run = [2]
    for i in run:
        tests[i]()



if __name__ == "__main__":
    #full_test()
    run_tests()
    #short_test()
