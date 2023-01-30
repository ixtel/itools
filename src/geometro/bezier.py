import numpy as np
from matplotlib.lines import Line2D
from scipy.special import binom


class BezierBuilder(object):
	"""Bézier curve interactive builder.
	"""
	
	def __init__(self, control_polygon, ax_bernstein):
		"""Constructor.
		Receives the initial control polygon of the curve.
		
		:param control_polygon:
		:param ax_bernstein:
		
		"""
		self.control_polygon = control_polygon
		self.xp = list(control_polygon.get_xdata())
		self.yp = list(control_polygon.get_ydata())
		self.canvas = control_polygon.figure.canvas
		self.ax_main = control_polygon.get_axes()
		self.ax_bernstein = ax_bernstein
		
		# Event handler for mouse clicking
		self.cid = self.canvas.mpl_connect('button_press_event', self)
		
		# Create Bézier curve
		line_bezier = Line2D([], [], c=control_polygon.get_markeredgecolor())
		self.bezier_curve = self.ax_main.add_line(line_bezier)
	
	def __call__(self, event):
		"""
		:param event:
		:return:
		"""
		# Ignore clicks outside axes
		if event.inaxes != self.control_polygon.axes:
			return
		
		# Add point
		self.xp.append(event.xdata)
		self.yp.append(event.ydata)
		self.control_polygon.set_data(self.xp, self.yp)
		
		# Rebuild Bézier curve and update canvas
		self.bezier_curve.set_data(*self._build_bezier())
		self._update_bernstein()
		self._update_bezier()
	
	def _build_bezier(self):
		"""
		:return:
		"""
		x, y = bezier(list(zip(self.xp, self.yp))).T
		return x, y
	
	def _update_bezier(self):
		"""
		:return:
		"""
		self.canvas.draw()
	
	def _update_bernstein(self):
		"""
		:return:
		"""
		n = len(self.xp) - 1
		t = np.linspace(0, 1, num=20)
		ax = self.ax_bernstein
		ax.clear()
		for kk in range(n + 1):
			ax.plot(t, bernstein(n, kk)(t))
		ax.set_title("Bernstein basis, N = {}".format(n))
		ax.set_xlim(0, 1)
		ax.set_ylim(0, 1)


def bernstein(n, k):
	"""
	Bernstein polynomial.
	:param n:
	:param k:
	:return:
	"""
	coeff = binom(n, k)
	
	def _bpoly(x):
		return coeff * x ** k * (1 - x) ** (n - k)
	
	return _bpoly


def bezier(points, num=20):
	"""
	Build Bézier curve from points.
	:param points:
	:param num:
	:return:
	"""
	n = len(points)
	t = np.linspace(0, 1, num=num)
	curve = np.zeros((num, 2))
	for ii in range(n):
		curve += np.outer(bernstein(n - 1, ii)(t), points[ii])
	return curve
