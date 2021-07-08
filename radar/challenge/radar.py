from kepler import pvt2kepler
from numpy import array, cos, pi, sin, sqrt
from numpy.linalg import norm
from skyfield.api import load
from datetime import datetime, timezone

from skyfield.units import Distance

ts = load.timescale()
t = ts.now()

μ = 3.986004418e5 #km^3/s^2

def parse_radar_data(file):
    pulses = []
    with open(file) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            if cnt > 1:
                pulse = line.strip().split()
                t = datetime.strptime(pulse[0], '%Y-%m-%d-%H:%M:%S.%f-%Z')
                t = t.replace(tzinfo=timezone.utc)
                pulse[0] = t
                pulse[1]= float(pulse[1])
                pulse[2]= float(pulse[2])
                pulse[3]= float(pulse[3])
                pulses.append(pulse)
            line = fp.readline()
            cnt += 1
    return pulses

def enu2ecef(loc,enu):
    φ = float(loc.latitude.radians)
    λ = float(loc.longitude.radians)
    h = float(loc.elevation.km)

    # WGS 84 parameters
    a = 6378.137 #km
    b = 6356.752314245 #km
    e2 = 1 - b*b/(a*a)
    N = a/sqrt(1-e2*sin(φ)*sin(φ))

    XYZ = array([
        (N+h)*cos(φ)*cos(λ),
        (N+h)*cos(φ)*sin(λ),
        (b*b/(a*a)*N+h)*sin(φ)
    ])

    enu = array(enu)
    
    M = [
        [-sin(λ),   -sin(φ)*cos(λ),  cos(φ)*cos(λ)],
        [cos(λ),    -sin(φ)*sin(λ),  cos(φ)*sin(λ)],
        [0,         cos(φ),          sin(φ)]
    ]

    ecef = M @ enu + XYZ

    return ecef

def estimateOrbit(location,pulses):
    #location = wgs84.latlon(8.7256, 167.715, 35)

    # Create an array of measured ICRF positions, z
    i = 0
    z = []
    while i < len(pulses):
        t  = ts.from_datetime(pulses[i][0])
        az = pulses[i][1]
        el = pulses[i][2]
        r  = pulses[i][3] # km

        # Convert AER to ICRF
        relPos = location.at(t).from_altaz(az_degrees=az, alt_degrees=el, distance=Distance(km=r))
        pos = location.at(t).position.km + relPos.position.km
        
        # Store ICRF positions into the measurement, z, array including time stamps
        z.append([pos[0], pos[1], pos[2], pulses[i][0]])
        i = i+1


    # Kalman Filter
    α = 0.5 # Gain for x
    i = 0   
    x0 = array([0,0,0,0,0,0])
    x1 = array([0,0,0,0,0,0])
    x0Dot = array([0,0,0,0,0,0])
    orbit = []
    
    while i < len(z):
        # Initial state estimate
        if i == 0:
            dt = (z[1][3] - z[0][3]).total_seconds()
            r0 = array(z[0][0:3])
            r = norm(r0)
            r1 = array(z[1][0:3])
            v = (r1 - r0)/dt

            x0 = array([
                z[i][0],
                z[i][1],
                z[i][2],
                v[0],
                v[1],
                v[2]
            ])

            x0Dot = array([
                x0[3],
                x0[4],
                x0[5],
                -μ*x0[0]/(r*r*r),
                -μ*x0[1]/(r*r*r),
                -μ*x0[2]/(r*r*r)
            ])

            orbit = pvt2kepler([x0[0],x0[1],x0[2],x0[3],x0[4],x0[5],z[i][3]])
            orbit[2] = orbit[2]*180/pi #i
            orbit[3] = orbit[3]*180/pi #RAAN
            orbit[4] = orbit[4]*180/pi #aop
            orbit[5] = orbit[5]*180/pi #true anomaly

        # Kalman filtered states
        else:
            # Predict next state with dynamics
            dt = (z[i][3] - z[i-1][3]).total_seconds()
            x0 = array([
                x0[0]+x0Dot[0]*dt,
                x0[1]+x0Dot[1]*dt,
                x0[2]+x0Dot[2]*dt,
                x0[3]+x0Dot[3]*dt,
                x0[4]+x0Dot[4]*dt,
                x0[5]+x0Dot[5]*dt
            ])
            r = norm(array(x0[0:3]))
            x0Dot = array([
                x0[3],
                x0[4],
                x0[5],
                -μ*x0[0]/(r*r*r),
                -μ*x0[1]/(r*r*r),
                -μ*x0[2]/(r*r*r)
            ])
            
            # Kalman gain
            α = 1/(i+1)
            #α = 0.5

            # Estimate next state with Kalman filter
            r0 = array(z[i-1][0:3])
            r = norm(r0)
            r1 = array(z[i][0:3])
            v = (r1 - r0)/dt

            x1 = array([
                x0[0]+α*(z[i][0]-x0[0]),
                x0[1]+α*(z[i][1]-x0[1]),
                x0[2]+α*(z[i][2]-x0[2]),
                x0[3]+α*(v[0]-x0[3]),
                x0[4]+α*(v[1]-x0[4]),
                x0[5]+α*(v[2]-x0[5])
            ])

            orbit = pvt2kepler([x1[0],x1[1],x1[2],x1[3],x1[4],x1[5],z[i][3]])
            orbit[2] = orbit[2]*180/pi #i
            orbit[3] = orbit[3]*180/pi #RAAN
            orbit[4] = orbit[4]*180/pi #aop
            orbit[5] = orbit[5]*180/pi #true anomaly

            # Set state for next iteration
            x0 = x1

        i = i+1

    return orbit