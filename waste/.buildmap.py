#!/usr/bin/python
import numpy as np
import cv2


def get_theta_old(x, y):
    if x == 0:
        if y > 0:
            theta = np.pi / 2
        elif y < 0:
            theta = np.pi * 3 / 2
        else:
            theta = 0
    elif x > 0:
        if y >= 0:
            theta = np.arctanH(y / x)
        else:
            theta = np.arctan(y / x) + 2 * np.pi
    else:
        theta = np.arctan(y / x) + np.pi
    return theta


def get_phi_old(p, theta, W, H, fov):
    if theta < np.pi / 4:
        p_max = W / (np.cos(theta) * 2)
    elif theta < np.pi * 3 / 4:
        p_max = H / (np.sin(theta) * 2)
    elif theta < np.pi * 5 / 4:
        p_max = -W / (np.cos(theta) * 2)
    elif theta < np.pi * 7 / 4:
        p_max = -H / (np.sin(theta) * 2)
    elif theta < np.pi * 2:
        p_max = W / (np.cos(theta) * 2)
    return p * fov / (p_max * 2)


def buildmap_0_old(Ws, Hs, Wd, Hd, fov=193.0):
    fov = fov * np.pi / 180.0
    R_max = np.sin(fov / 2) / (1 + np.cos(fov / 2))
    xmap = np.zeros((Hs, Ws), np.float32)
    ymap = np.zeros((Hs, Ws), np.float32)
    for ys in range(Hs):
        for xs in range(Ws):
            # cartesian coordinates of the projected (square) image
            y_proj = Hs / 2.0 - ys
            x_proj = xs - Ws / 2.0
            p = np.sqrt(x_proj ** 2 + y_proj ** 2)

            # spherical coordinates
            theta = get_theta_old(x_proj, y_proj)
            phi = get_phi_old(x_proj, y_proj, Ws, Hs, fov)

            # polar coordinates (of the fisheye image)
            R = np.sin(phi) / (1 + np.cos(phi))

            # cartesian coordinates of the fisheye image
            y_fish = R * np.sin(theta)
            x_fish = R * np.cos(theta)

            yd = (Hd - y_fish * Hd / R_max) / 2.0
            xd = (Wd + x_fish * Wd / R_max) / 2.0
            xmap[ys, xs] = xd
            ymap[ys, xs] = yd
    return xmap, ymap


def buildmap_1_old(Ws, Hs, Wd, Hd, fov=193.0):
    fov = fov * np.pi / 180.0
    R_max = np.sin(fov / 2) / (1 + np.cos(fov / 2))
    xmap = np.zeros((Hs, Ws), np.float32)
    ymap = np.zeros((Hs, Ws), np.float32)
    for ys in range(Hs):
        for xs in range(Ws):
            # cartesian coordinates of the projected (square) image
            y_proj = Hs / 2.0 - ys
            x_proj = xs - Ws / 2.0
            #p = np.sqrt(x_proj ** 2 + y_proj ** 2)

            # spherical coordinates
            theta, phi = get_theta_phi(x_proj, y_proj, Ws, Hs, fov)

            # polar coordinates (of the fisheye image)
            R = np.sin(phi) / (1 - np.cos(phi))

            # cartesian coordinates of the fisheye image
            y_fish = R * np.sin(theta)
            x_fish = R * np.cos(theta)

            yd = (Hd - y_fish * Hd / R_max) / 2.0
            xd = (Wd + x_fish * Wd / R_max) / 2.0
            xmap[ys, xs] = xd
            ymap[ys, xs] = yd
    return xmap, ymap


def get_theta_phi_1(x_proj, y_proj, W, H, fov):
    theta_alt = x_proj * fov / W
    phi_alt = y_proj * np.pi / H

    x = np.sin(theta_alt) * np.cos(phi_alt)
    y = np.sin(phi_alt)
    z = -np.cos(theta_alt) * np.cos(phi_alt)

    return np.arctan2(y, x), np.arctan2(np.sqrt(x**2 + y**2), z)


def buildmap_1(Ws, Hs, Wd, Hd, fov=180.0):
    fov = fov * np.pi / 180.0
    p_max = np.sin(fov / 2.0) / (1 + np.cos(fov / 2.0))

    # cartesian coordinates of the projected (square) image
    ys, xs = np.indices((Hs, Ws), np.float32)
    y_proj = Hs / 2.0 - ys
    x_proj = xs - Ws / 2.0

    # spherical coordinates
    theta, phi = get_theta_phi_1(x_proj, y_proj, Ws, Hs, fov)

    # polar coordinates (of the fisheye image)
    p = np.sin(phi) / (1 - np.cos(phi))

    # cartesian coordinates of the fisheye image
    y_fish = p * np.sin(theta)
    x_fish = p * np.cos(theta)

    ymap = (Hd - y_fish * Hd / p_max) / 2.0
    xmap = (Wd + x_fish * Wd / p_max) / 2.0
    return xmap, ymap
