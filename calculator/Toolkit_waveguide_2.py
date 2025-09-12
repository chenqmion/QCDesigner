import numpy as np
import mpmath
import scipy.constants as const
from dataclasses import dataclass, field

@dataclass
class MyWaveguide:
    '''material'''
    epsilon_r1: float = 11.9
    h1: float = None
    epsilon_r2: float = 3.9
    h2: float = None
    epsilon_r_eff: float = None
    mu_r: float = 1.0
    '''geometry'''
    a: float = None # Width of center conductor (m)
    b: float = None # Width of gap (m)
    '''microwave'''
    c_CPW: float = None # Capacitance per length (F/m)
    l_CPW: float = None # Inductance per length (H/m)
    v_phase: float = None # Phase velocity (m/s)
    Z0: float = None # Characteristic impedance (Ohm)
    '''resonance'''
    l: float = None # Length (m)
    w0: float = None # Fundamental mode (2pi*Hz)
    
    def __post_init__(self):
        if (self.epsilon_r1 != None) and (self.a != None) and (self.b != None):
            k0 = self.a/(self.a+2*self.b) # air
            ellipk_0 = mpmath.ellipk(k0**2)/mpmath.ellipk(1-k0**2)
            c_0 = 4*const.epsilon_0*float(ellipk_0)
            
            if self.h1 != None: # substrate 1
                k1 = mpmath.sinh(const.pi*self.a/(4*self.h1))*mpmath.csch(const.pi*(self.a+2*self.b)/(4*self.h1))
                ellipk_1 = mpmath.ellipk(k1**2)/mpmath.ellipk(1-k1**2)
                
                c_1 = 2*const.epsilon_0*(self.epsilon_r1-1)*float(ellipk_1)
                q1 = ellipk_1/(2*ellipk_0)
            else:
                c_1 = 2*const.epsilon_0*(self.epsilon_r1-1)*float(ellipk_0)
                q1 = 1/2
                
            if self.h2 != None:  # substrate 2
                k2 = mpmath.sinh(const.pi*self.a/(4*self.h2))*mpmath.csch(const.pi*(self.a+2*self.b)/(4*self.h2))
                ellipk_2 = mpmath.ellipk(k2**2)/mpmath.ellipk(1-k2**2)
                if ellipk_2 == 0:
                    ellipk_2 = -const.pi/(2*mpmath.ln(k2/4)) # Taylor expansion of ellipk_2 for small k2
                
                c_2 = 2*const.epsilon_0*(self.epsilon_r2-self.epsilon_r1)*float(ellipk_2)
                q2 = ellipk_2/(2*ellipk_0)
            else:
                c_2 = 0
                q2 = 0
            
            self.c_CPW = c_0 + c_1 + c_2
            self.epsilon_r_eff = 1 + float(q1)*(self.epsilon_r1-1) + float(q2)*(self.epsilon_r2-self.epsilon_r1)
            self.v_phase = const.c/np.sqrt(self.epsilon_r_eff*self.mu_r)
            self.l_CPW = 1/(self.c_CPW*(self.v_phase**2))
            self.Z0 = 1/(self.c_CPW*self.v_phase)
        
        if (self.l_CPW == None):
            if (self.c_CPW != None) and (self.v_phase != None):
                self.l_CPW = 1/(self.c_CPW*(self.v_phase**2))
            elif (self.c_CPW != None) and (self.Z0 != None):
                self.l_CPW = self.c_CPW * (self.Z0**2)
            elif (self.v_phase != None) and (self.Z0 != None):
                self.l_CPW = self.Z0/self.v_phase
        
        if (self.c_CPW == None):
            if (self.l_CPW != None) and (self.v_phase != None):
                self.c_CPW = 1/(self.l_CPW*(self.v_phase**2))
            elif (self.l_CPW != None) and (self.Z0 != None):
                self.c_CPW = self.l_CPW / (self.Z0**2)
            elif (self.v_phase != None) and (self.Z0 != None):
                self.c_CPW = 1/(self.Z0*self.v_phase)
        
        if (self.v_phase == None):
            self.v_phase = 1/np.sqrt(self.l_CPW*self.c_CPW)
            
        if (self.Z0 == None):
            self.Z0 = np.sqrt(self.l_CPW/self.c_CPW)
        
        if (self.w0 != None):
            self.l = const.pi*self.v_phase/self.w0
        
        if (self.l != None):
            self.w0 = const.pi*self.v_phase/self.l

#%% example
x = MyWaveguide(a=10.0E-6, b=6.0E-6, w0=8.0E9*(2*const.pi), h1 = 675E-6)

# x = MyWaveguide(a=10.0E-6, b=6.0E-6, w0=5.0E9*(2*const.pi))

# x = MyWaveguide(a=0.01E-6, b=2000E-6, w0=8.0E9*(2*const.pi), h1 = 675E-6)

# x = MyWaveguide(a=35E-6, b=6E-6, w0=8.0E9*(2*const.pi))
# x = MyWaveguide(a=29E-6, b=5E-6, w0=8.0E9*(2*const.pi))

# x = MyWaveguide(a=6E-6, b=12E-6, w0=8.0E9*(2*const.pi))
# x = MyWaveguide(a=10E-6, b=20E-6, w0=8.0E9*(2*const.pi))

# y = MyWaveguide(a=4E-6, b=30E-6, w0=8.0E9*(2*const.pi), h1 = 675E-6, h2 = 300E-9)
# y = MyWaveguide(a=6E-6, b=48E-6, w0=8.0E9*(2*const.pi), h1 = 675E-6, h2 = 300E-9)
# print(y.Z0)

# x = MyWaveguide(a=12.0E-6, b=7.0E-6, w0=6.0E9*(2*const.pi), h1 = 675E-6, h2 = 300E-9)

# x = MyWaveguide(a=10.0E-6, b=6E-6, w0=8E9*(2*const.pi), h1 = 675E-6, h2 = 250E-9)
# print(x.l*1E6/2)
# print(x.l*1E6/2 * 0.05)
# x = MyWaveguide(a=4E-6, b=30E-6, w0=5E9*(2*const.pi))
# y = MyWaveguide(a=17E-6, b=3E-6, w0=5E9*(2*const.pi))
# print(y.Z0)

# x = []
# y = []

# w_list = np.array([4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8]) * (2*np.pi)*1E9
# C_in = 48.9 * 1E-15
# for w in w_list:
#     w_new = w + 2*50*C_in*(w**2)/np.pi

#     wg = MyWaveguide(a=10.0E-6, b=6.0E-6, w0=w_new, h1 = 675E-6, h2 = 300E-9)
#     print(wg.l*1E6/2)

    

