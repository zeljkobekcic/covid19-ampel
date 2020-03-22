import numpy as np
from scipy.optimize import curve_fit


def morgen(days, population):
    popt, _ = curve_fit(
        f=logistic_model,
        xdata=days.reset_index()["days"],
        ydata=days["AnzahlFall"],
        p0=[
            .7 * population,  # max infected
            3,  # infection speed,
            days["AnzahlFall"].idxmax(),  # max infections day
        ],
        bounds=([.6 * population, 2, days["AnzahlFall"].idxmax()], [.8 * population, 4, 80])
    )
    maxinf, infspeed, maxday = popt
    return logistic_model(days["AnzahlFall"].idxmax() + 1, maxinf, infspeed, maxday)


def logistic_model(x, max_infected, infection_speed, max_infections_day):
    return max_infected / (1 + np.exp(-(x - max_infections_day) / infection_speed))
