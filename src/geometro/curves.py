import numpy as np
from scipy.special import comb


def bernstein_poly(i, n, t):
	"""
	The Bernstein polynomial of n, i as a function of t
	:param i:
	:param n:
	:param t:
	:return:
	"""
	return comb(n, i) * (t ** (n - i)) * (1 - t) ** i


def bezier_curve(points, n_times=50):
	"""
	Given a set of control points, return the
		bezier curve defined by the control points.
		
		points should be a list of lists, or list of tuples
		such as [
			[1,1],
			[2,3],
			[4,5], ..[Xn, Yn]
			]
		n_times is the number of time steps, defaults to 1000
		
		See http://processingjs.nihongoresources.com/bezierinfo/
	:param points:
	:param n_times:
	:return:
	"""
	n_points = len(points)
	x_points = np.array([int(p['x']) for p in points])
	y_points = np.array([int(p['y']) for p in points])
	
	t = np.linspace(0.0, 1.0, n_times)
	
	polynomial_array = np.array([bernstein_poly(i, n_points - 1, t) for i in range(0, n_points)])
	
	xvals = np.dot(x_points, polynomial_array)
	yvals = np.dot(y_points, polynomial_array)
	
	xvals = reversed(xvals)
	yvals = reversed(yvals)
	
	xvals = [int(p) for p in xvals]
	yvals = [int(p) for p in yvals]
	curve = []
	for i, x in enumerate(xvals):
		curve.append({
			'x': x,
			'y': yvals[i]
		})
	return curve, xvals, yvals
