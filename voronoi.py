# Inspired by https://www.cs.hmc.edu/~mbrubeck/voronoi.html
from queue import PriorityQueue
from math import sqrt
import math
import matplotlib.pyplot as plt
import numpy as np
import sys
import time

# --------------------------------------------------------- #
#                                                           #
#                   Useful Datatypes                        #
#                                                           #
# --------------------------------------------------------- #


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set_coords(self, x, y):
        self.x = x
        self.y = y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y


class BoundingBox:
    def __init__(self, point1: Point, point2: Point):
        self.min = point1
        self.max = point2


class Arc:
    def __init__(self, point, prev_arc=None, next_arc=None):
        self.point = point
        self.prev = prev_arc
        self.next = next_arc
        self.event = None
        self.edge1 = None
        self.edge2 = None


class Event:
    def __init__(self, x, point: Point, arc: Arc, is_site: bool):
        self.is_site = is_site
        self.x = x
        self.point = point
        self.arc = arc
        self.valid = True


class Edge:
    def __init__(self, point: Point):
        self.start = point
        self.end = None
        self.done = False

    def complete(self, point: Point):
        if self.done:
            return
        self.end = point
        self.done = True

# --------------------------------------------------------- #
#                                                           #
#                   Utility Functions                       #
#                                                           #
# --------------------------------------------------------- #


def intersect(point: Point, arc: Arc):
    """
    Checks if a new parabola with focus point intersects with an existing parabola arc

    :param point: Focus of new parabola
    :param arc: Existing parabola
    :return: Intersection with arc or None if no intersection
    """
    if arc is None or arc.point.x == point.x:
        return False, None
    a = 0.0
    b = 0.0
    if arc.prev is not None:
        a = (intersection(arc.prev.point, arc.point, 1.0 * point.x)).y
    if arc.next is not None:
        b = (intersection(arc.point, arc.next.point, 1.0 * point.x)).y
    if (arc.prev is None or a <= point.y) and (arc.next is None or point.y <= b):
        px = 1.0 * (arc.point.x ** 2 + (arc.point.y - point.y) ** 2 - point.x ** 2) / (2 * arc.point.x - 2 * point.x)
        return True, Point(px, point.y)
    return False, None


def intersection(point1, point2, dist):
    """
    Finds intersection between two parabolic arcs.

    :param point1: First Focus
    :param point2: Second Focus
    :param dist: Distance x
    :return: Point of intersection or None if no intersection
    """
    p = point1
    if point1.x == point2.x:
        py = (point1.y + point2.y) / 2.0
    elif point2.x == dist:
        py = point2.y
    elif point1.x == dist:
        py = point1.y
        p = point2
    else:
        # use quadratic formula
        z0 = 2.0 * (point1.x - dist)
        z1 = 2.0 * (point2.x - dist)

        a = 1.0 / z0 - 1.0 / z1
        b = -2.0 * (point1.y / z0 - point2.y / z1)
        c = 1.0 * (point1.y ** 2 + point1.x ** 2 - dist ** 2) / z0 - 1.0 * (point2.y ** 2 + point2.x ** 2 - dist ** 2) / z1

        py = 1.0 * (-b - sqrt(b * b - 4 * a * c)) / (2 * a)

    px = 1.0 * (p.x ** 2 + (p.y - py) ** 2 - dist ** 2) / (2 * p.x - 2 * dist)
    res = Point(px, py)
    return res


def circle(a, b, c):
    """
    CCW and finding center of circle defined by three points

    :param a: First point
    :param b: Second point
    :param c: Third point
    :return: Bool for degenerate cases, CCW, and center of circle
    """
    if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0:
        return False, None, None

    # Algorithm from O'Rourke 2ed p. 189
    A = b.x - a.x
    B = b.y - a.y
    C = c.x - a.x
    D = c.y - a.y
    E = A * (a.x + b.x) + B * (a.y + b.y)
    F = C * (a.x + c.x) + D * (a.y + c.y)
    G = 2 * (A * (c.y - b.y) - B * (c.x - b.x))

    if G == 0:
        return False, None, None  # Points are co-linear

    # point o is the center of the circle
    ox = 1.0 * (D * E - B * F) / G
    oy = 1.0 * (A * F - C * E) / G

    # o.x plus radius equals max x coord
    x = ox + sqrt((a.x - ox) ** 2 + (a.y - oy) ** 2)
    o = Point(ox, oy)

    return True, x, o


class Voronoi:
    def __init__(self, sites):
        self.event_queue = PriorityQueue()
        self.beach_line = None  # root of binary tree of parabolic arcs
        self.output = []
        self.vertices = []  # Daftar untuk menyimpan vertex

        # bounding box
        x1 = 0.0
        x2 = 0.0
        y1 = 0.0
        y2 = 0.0

        # insert points to site event
        for site in sites:
            event = Event(site.x, site, None, True)
            self.event_queue.put((event.x, event))
            # keep track of bounding box size
            if site.x < x1:
                x1 = site.x
            if site.y < y1:
                y1 = site.y
            if site.x > x2:
                x2 = site.x
            if site.y > y2:
                y2 = site.y

        # add margins to the bounding box
        dx = (x2 - x1 + 1) / 5.0
        dy = (y2 - y1 + 1) / 5.0
        x1 = x1 - dx
        x2 = x2 + dx
        y1 = y1 - dy
        y2 = y2 + dy

        self.bbox = BoundingBox(Point(x1, y1), Point(x2, y2))

    def compute(self):
        while not self.event_queue.empty():
            next_event = self.event_queue.get()[1]
            if next_event.is_site:
                self.handle_site(next_event.point)
            else:
                self.handle_event(next_event)
        self.complete_edges()

    def handle_site(self, point):
        self.insert_arc(point)

    def handle_event(self, event):
        if event.valid:
            # start new edge
            edge = Edge(event.point)
            self.output.append(edge)

            # Simpan vertex
            self.vertices.append(event.point)

            # remove associated arc (parabola)
            arc = event.arc
            if arc.prev is not None:
                arc.prev.next = arc.next
                arc.prev.edge2 = edge
            if arc.next is not None:
                arc.next.prev = arc.prev
                arc.next.edge1 = edge

            # finish the edges before and after a
            if arc.edge1 is not None:
                arc.edge1.complete(event.point)
            if arc.edge2 is not None:
                arc.edge2.complete(event.point)

            # recheck circle events on either side of p
            if arc.prev is not None:
                self.check_circle_event(arc.prev)
            if arc.next is not None:
                self.check_circle_event(arc.next)

    def insert_arc(self, point: Point):
        if self.beach_line is None:
            self.beach_line = Arc(point)
        else:
            arc = self.beach_line
            while arc is not None:
                flag, z = intersect(point, arc)
                if flag:
                    flag, zz = intersect(point, arc.next)
                    if arc.next is not None and not flag:
                        arc.next.prev = Arc(arc.point, arc, arc.next)
                        arc.next = arc.next.prev
                    else:
                        arc.next = Arc(arc.point, arc)
                    arc.next.edge2 = arc.edge2
                    arc.next.prev = Arc(point, arc, arc.next)
                    arc.next = arc.next.prev
                    arc = arc.next

                    edge1 = Edge(z)
                    self.output.append(edge1)
                    arc.prev.edge2 = arc.edge1 = edge1

                    edge2 = Edge(z)
                    self.output.append(edge2)
                    arc.next.edge1 = arc.edge2 = edge2

                    self.check_circle_event(arc)
                    self.check_circle_event(arc.prev)
                    self.check_circle_event(arc.next)
                    return
                arc = arc.next
            arc = self.beach_line
            while arc.next is not None:
                arc = arc.next
            arc.next = Arc(point, arc)
            start = Point(self.bbox.min.x, (arc.next.point.y + arc.point.y) / 2.0)

            edge = Edge(start)
            arc.edge2 = arc.next.edge1 = edge
            self.output.append(edge)

    def check_circle_event(self, arc: Arc):
        if arc.event is not None and arc.event.x != self.bbox.min.x:
            arc.event.valid = False
        arc.event = None
        if arc.prev is None or arc.next is None:
            return
        flag, x, center = circle(arc.prev.point, arc.point, arc.next.point)
        if flag and x > self.bbox.min.x:
            arc.event = Event(x, center, arc, False)
            self.event_queue.put((arc.event.x, arc.event))

    def complete_edges(self):
        dist = self.bbox.max.x + (self.bbox.max.x - self.bbox.min.x) + (self.bbox.max.y - self.bbox.min.y)
        arc = self.beach_line
        while arc.next is not None:
            if arc.edge2 is not None:
                point = intersection(arc.point, arc.next.point, dist * 2.0)
                arc.edge2.complete(point)
            arc = arc.next

    def print_output(self):
        for edge in self.output:
            point1 = edge.start
            point2 = edge.end
            print(point1.x, point1.y, point2.x, point2.y)

    def get_output(self):
        output = []
        for edge in self.output:
            point1 = edge.start
            point2 = edge.end
            output.append((point1.x, point1.y, point2.x, point2.y))
        return output
    
    def print_vertices(self):
        vertices = []
        for vertex in self.vertices:
            vertices.append((vertex.x, vertex.y))

        return vertices
    
def distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def largest_circle(sites, vertices):
    """
    Determine the largest circle that boundaries with at least 3 sites,
    centered at one of the Voronoi vertices.

    :param sites: List of site tuples (x, y).
    :param vertices: List of Voronoi vertex tuples (x, y).
    :return: List of tuples [(center, radius), ...] for the largest circles.
    """
    largest_circles = []
    max_radius = 0

    for vertex in vertices:
        # Compute distances to all sites
        distances = [distance(vertex, site) for site in sites]
        
        # Sort distances in ascending order and take the third smallest distance
        distances.sort()
        radius = distances[2]  # Distance to the third closest site

        if radius > max_radius:
            # Found a larger radius, reset the largest_circles list
            max_radius = radius
            largest_circles = [(vertex, radius)]
        elif radius == max_radius:
            # If the radius ties with the max, add to the list
            largest_circles.append((vertex, radius))

    return largest_circles