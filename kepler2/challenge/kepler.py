from numpy import arccos, arctan, array, cos, cross, dot, pi, sin, sqrt, tan
from numpy.linalg import norm
from datetime import datetime, timedelta

μ = 3.986004418e5 #km^3/s^2

# Solve Kepler's equation
def solveKepler(M,e):
    E = M
    dE = pi
    while dE > 1e-6:
        E0 = E
        E = M + e*sin(E)
        dE = abs(E-E0)
    return E

# Rotation Matrices
def Rx(θ):
    mat = array([
        [1,         0,          0],
        [0,         cos(θ),     sin(θ)],
        [0,         -sin(θ),     cos(θ)]]
    )
    return mat

def Ry(θ):
    mat = array([
        [cos(θ),    0,          -sin(θ)],
        [0,         1,          0],
        [sin(θ),   0,          cos(θ)]]
    )
    return mat

def Rz(θ):
    mat = array([
        [cos(θ),    sin(θ),    0],
        [-sin(θ),    cos(θ),     0],
        [0,         0,          1]]
    )
    return mat

def pvt2kepler(pvt):
    # convert pvt to elements...
    assert isinstance(pvt[6], datetime), "pvt[6] is not a valid datetime object"
    t0 = pvt[6]
    
    r_ = array(pvt[0:3])
    v_ = array(pvt[3:6])

    r = norm(r_)
    
    h_ = cross(r_,v_)
    h = norm(h_)
    e_ = cross(v_,h_)/μ - r_/r
    e = norm(e_)

    p = h*h/μ

    a = p /(1-e*e)
    a = norm(a)

    i = arccos(h_[2]/h)

    Ω=0
    n_ = [-h_[1],h_[0],0]
    n = norm(n_)
    if n_[1] >= 0:
        Ω = arccos(n_[0]/n)
    if n_[1] < 0:
        Ω = 2*pi - arccos(n_[0]/n)

    ω = arccos(dot(n_,e_) / (n*e))
    if e_[2] < 0:
        ω = 2*pi - ω
        
    
    υ = arccos(dot(e_,r_)/(e*r))
    if dot(r_,v_) < 0:
        υ = 2*pi - υ

    # [a(km) e i(rad) Ω(rad) ω(rad) υ(rad)]
    elements = [a, e, i, Ω, ω, υ, t0]
    return elements

def kepler2pvt(elements):
    [a, e, i, Ω, ω, υ, t0] = elements
    assert isinstance(t0, datetime), "elements[6] is not a valid datetime object"

    E = 2*arctan(tan(υ/2)/sqrt((1+e)/(1-e)))

    r = a*(1-e*cos(E))

    o_ = r*array([cos(υ), sin(υ), 0])
    oDot_ = sqrt(μ*a)/r*array([-sin(E), sqrt(1-e*e)*cos(E), 0])

    # Convert to ICRF
    r_ = Rz(-Ω) @ Rx(-i) @ Rz(-ω) @ o_
    v_ = Rz(-Ω) @ Rx(-i) @ Rz(-ω) @ oDot_

    return [r_[0],r_[1],r_[2],v_[0],v_[1],v_[2],t0]


# Propagate elements by dt seconds
def prop(dt, elements):
    [a, e, i, Ω, ω, υ, t0] = elements
    assert isinstance(t0, datetime), "elements[6] is not a valid datetime object"

    n = sqrt(μ/(a*a*a))
    E = arctan(sqrt(1-e*e)*sin(υ)/(e+cos(υ)))
    M = E - e*sin(E)
    M = M + n*(dt)

    # Kepler's equation
    E = solveKepler(M,e)

    υ = 2*arctan(sqrt((1+e)/(1-e))*tan(E/2))
    #print(υ)

    # New epoch
    dt = timedelta(0,dt)
    t1 = t0 + dt
    
    return [a, e, i, Ω, ω, υ, t1]