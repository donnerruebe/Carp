from __future__ import division, print_function

import math

import numpy

__version__ = '0.1'


def unit_vector(v):
    return v / numpy.linalg.norm(v)

def identity_matrix():
    return numpy.identity(4)


def translation_matrix(direction):
    M = numpy.identity(4)
    M[:3, 3] = direction[:3]
    return M


def translation_from_matrix(matrix):
    return numpy.array(matrix, copy=False)[:3, 3].copy()

def rotation_from_euler(angles):
    result = numpy.identity(4)
    if angles == (0,0,0):
        return result
    
    cos_psi = math.cos(angles[0]);
    sin_psi = math.sin(angles[0]);
    cos_theta = math.cos(angles[1]);
    sin_theta = math.sin(angles[1]);
    cos_phi = math.cos(angles[2]);
    sin_phi = math.sin(angles[2]);

    result[0,0] = cos_theta * cos_psi;
    result[0,1] = -cos_phi * sin_psi + sin_phi * sin_theta * cos_psi;
    result[0,2] = sin_phi * sin_psi + cos_phi * sin_theta * cos_psi;
      
    result[1,0] = cos_theta * sin_psi;
    result[1,1] = cos_phi * cos_psi + sin_phi * sin_theta * sin_psi;
    result[1,2] = -sin_phi * cos_psi + cos_phi * sin_theta * sin_psi;

    result[2,0] = -sin_theta;
    result[2,1] = sin_phi * cos_theta;
    result[2,2] = cos_phi * cos_theta;
    return result

def rotation_from_euler_deg(angles_in_degrees):
    angles_in_radians = [math.radians(angles_in_degrees[0]), math.radians(angles_in_degrees[1]), math.radians(angles_in_degrees[2])]
    return rotation_from_euler(angles_in_radians)

def rotation_matrix(angle, axis, center=None):
    sina = math.sin(angle)
    cosa = math.cos(angle)
    axis = unit_vector(axis[:3])
    # rotation matrix around unit vector
    R = numpy.diag([cosa, cosa, cosa])
    R += numpy.outer(axis, axis) * (1.0 - cosa)
    axis *= sina
    R += numpy.array([[ 0.0, -axis[2], axis[1]],
                      [ axis[2], 0.0, -axis[0]],
                      [-axis[1], axis[0], 0.0]])
    M = numpy.identity(4)
    M[:3, :3] = R
    if center is not None:
        # rotation not around origin
        center = numpy.array(center[:3], dtype=numpy.float64, copy=False)
        M[:3, 3] = center - numpy.dot(R, center)
    return M

def rotation_matrix_deg(angle_in_degrees, axis, center=None):
    angle_in_radians = math.radians(angle_in_degrees) 
    return rotation_matrix(angle_in_radians, axis, center)

def rotation_from_matrix(matrix):
    R = numpy.array(matrix, dtype=numpy.float64, copy=False)
    R33 = R[:3, :3]
    # direction: unit eigenvector of R33 corresponding to eigenvalue of 1
    w, W = numpy.linalg.eig(R33.T)
    i = numpy.where(abs(numpy.real(w) - 1.0) < 1e-8)[0]
    if not len(i):
        raise ValueError("no unit eigenvector corresponding to eigenvalue 1")
    direction = numpy.real(W[:, i[-1]]).squeeze()
    # point: unit eigenvector of R33 corresponding to eigenvalue of 1
    w, Q = numpy.linalg.eig(R)
    i = numpy.where(abs(numpy.real(w) - 1.0) < 1e-8)[0]
    if not len(i):
        raise ValueError("no unit eigenvector corresponding to eigenvalue 1")
    point = numpy.real(Q[:, i[-1]]).squeeze()
    point /= point[3]
    # rotation angle depending on direction
    cosa = (numpy.trace(R33) - 1.0) / 2.0
    if abs(direction[2]) > 1e-8:
        sina = (R[1, 0] + (cosa-1.0)*direction[0]*direction[1]) / direction[2]
    elif abs(direction[1]) > 1e-8:
        sina = (R[0, 2] + (cosa-1.0)*direction[0]*direction[2]) / direction[1]
    else:
        sina = (R[2, 1] + (cosa-1.0)*direction[1]*direction[2]) / direction[0]
    angle = math.atan2(sina, cosa)
    return angle, direction, point


def scale_matrix(factor, origin=None, direction=None):
    if direction is None:
        # uniform scaling
        M = numpy.diag([factor, factor, factor, 1.0])
        if origin is not None:
            M[:3, 3] = origin[:3]
            M[:3, 3] *= 1.0 - factor
    else:
        # nonuniform scaling
        direction = unit_vector(direction[:3])
        factor = 1.0 - factor
        M = numpy.identity(4)
        M[:3, :3] -= factor * numpy.outer(direction, direction)
        if origin is not None:
            M[:3, 3] = (factor * numpy.dot(origin[:3], direction)) * direction
    return M


def scale_from_matrix(matrix):
    M = numpy.array(matrix, dtype=numpy.float64, copy=False)
    M33 = M[:3, :3]
    factor = numpy.trace(M33) - 2.0
    try:
        # direction: unit eigenvector corresponding to eigenvalue factor
        w, V = numpy.linalg.eig(M33)
        i = numpy.where(abs(numpy.real(w) - factor) < 1e-8)[0][0]
        direction = numpy.real(V[:, i]).squeeze()
        direction /= numpy.linalg.norm(direction)
    except IndexError:
        # uniform scaling
        factor = (factor + 2.0) / 3.0
        direction = None
    # origin: any eigenvector corresponding to eigenvalue 1
    w, V = numpy.linalg.eig(M)
    i = numpy.where(abs(numpy.real(w) - 1.0) < 1e-8)[0]
    if not len(i):
        raise ValueError("no eigenvector corresponding to eigenvalue 1")
    origin = numpy.real(V[:, i[-1]]).squeeze()
    origin /= origin[3]
    return factor, origin, direction

def rotation_translation_scale_matrix(euler_angles_in_degrees, position, scale):
    result = rotation_from_euler_deg(euler_angles_in_degrees)
    result *= scale
    result[:3, 3] = position[:3]
    result[3, 3] = 1.0
    return result
    