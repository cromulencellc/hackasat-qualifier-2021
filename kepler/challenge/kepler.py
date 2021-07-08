from numpy import arccos, array, cross, dot, pi
from numpy.linalg import norm

def pvt2kepler(pvt):
    # convert pvt to elements...
    μ = 3.986004418e5 #km^3/s^2
    
    r = array(pvt[0:3])
    v = array(pvt[3:6])
    
    h = cross(r,v)
    e_ = cross(v,h)/μ - r/norm(r)
    e = norm(e_)

    p = h*h/μ

    a = p /(1-e*e)
    a = norm(a)

    i = arccos(h[2]/norm(h))*180/pi

    Ω=0
    n = [-h[1],h[0],0]
    if n[1] >= 0:
        Ω = arccos(n[0]/norm(n))
    if n[1] < 0:
        Ω = 2*pi - arccos(n[0]/norm(n))
    Ω = Ω * 180/pi

    ω = arccos(dot(n,e_) / (norm(n)*e)) * 180/pi
    if e_[2] < 0:
        ω = 360 - ω
        
    
    υ = arccos(dot(e_,r)/(e*norm(r))) * 180/pi
    if dot(r,v) < 0:
        υ = 360 - υ

    '''
    print("a:",a)
    print("e:",e)
    print("i:",i)
    print("Ω:",Ω)
    print("ω:",ω)
    print("υ:",υ)
    '''

    # [a(km) e i(deg) Ω(deg) ω(deg) υ(deg)]
    #elements = [24732.886033, 0.706807, 0.118, 90.227, 226.587, 90.390]
    elements = [a, e, i, Ω, ω, υ]
    return elements