"""
FLC: Predicting the Cause of Fire
Let 3 fuzzy inputs (max color slope(C), max area slope(A)) and one fuzzy
output cause of fire(CF) 0-explosion 300-shortcircuit be there.

X: Universe of discourse [0,300]
Partitions: 
    NL: Open left MF (a = 30, b = 90) 
    NS: Traingular(a = 30, b = 90, c = 150)
    ZE: Traingular(a = 90, b = 150, c = 210)
    PS: Traingular(a = 150, b = 210, c = 270)
    PL: Open right (a = 210, b = 270) 
    
Rules(to be fine tuned)
R1: A is NL and C is NL then CF is NL
R2: A is NL and C is NS then CF is NL
R3: A is NL and C is ZE then CF is NS
R4: A is NL and C is PS then CF is NS
R5: A is NL and C is PL then CF is NS

R6: A is NS and C is NL then CF is NL
R7: A is NS and C is NS then CF is NL
R8: A is NS and C is ZE then CF is NS
R9: A is NS and C is PS then CF is NS
R10: A is NS and C is PL then CF is NS

R11: A is ZE and C is NL then CF is NL
R12: A is ZE and C is NS then CF is NS
R13: A is ZE and C is ZE then CF is NS
R14: A is ZE and C is PS then CF is ZE
R15: A is ZE and C is PL then CF is ZE

R16: A is PS and C is NL then CF is NS
R17: A is PS and C is NS then CF is ZE
R18: A is PS and C is ZE then CF is PS
R19: A is PS and C is PS then CF is PS
R20: A is PS and C is PL then CF is PL

R21: A is PL and C is NL then CF is PS
R22: A is PL and C is NS then CF is PL
R23: A is PL and C is ZE then CF is PL
R24: A is PL and C is PS then CF is PL
R25: A is PL and C is PL then CF is PL

"""
import matplotlib.pyplot as plt
import os
import color_detection as cd

#Functions for open left-Right fuzzyfication  
def openLeft(x,alpha, beta):
    if x<alpha:
        return 1
    if alpha<x and x<=beta:
        return (beta - x)/(beta - alpha)
    else:
        return 0
    
def openRight(x,alpha, beta):
    if x<alpha:
        return 0
    if alpha<x and x<=beta:
        return (x-alpha)/(beta - alpha)
    else:
        return 1

# Function for traingular fuzzyfication  
def triangular(x,a,b,c):
    return max(min((x-a)/(b-a), (c-x)/(c-b)),0)

# Rules implementation
def compare(CF1, CF2):
    CF = 0
    if CF1>CF2 and CF1 !=0 and CF2 !=0:
        CF = CF2
    else:
        CF = CF1
    
    if CF1 == 0 and CF2 !=0:
        CF = CF2
        
    if CF2 == 0 and CF1 !=0:
        CF = CF1
        
    return CF


#Fuzzy Partition 
def partition(x):
    NL = 0; NS = 0; ZE = 0; PS = 0; PL = 0
    
    if x>=0 and x<90:
        NL = openLeft(x,30,90)
    if x>30 and x<150:
        NS = triangular(x,30,90,150)
    if x>90 and x<210:
        ZE = triangular(x,90,150,210)
    if x>150 and x<270:
        PS = triangular(x,150,210,270)
    if x>210 and x<=300:
        PL = openRight(x,210,270)

    return NL,NS,ZE,PS,PL

def rule(NLCL,NSCL,ZECL,PSCL,PLCL,NLAR,NSAR,ZEAR,PSAR,PLAR):
    PLCF1 = min(PLAR,PLCL) 
    PLCF2 = min(PLAR,PSCL)
    PLCF3 = min(PLAR,ZECL)
    PLCF4 = min(PLAR,NSCL)
    PLCF5 = min(PSAR,PLCL)
    PLCF = compare(PLCF1, compare(PLCF2, compare(PLCF3, compare(PLCF4, PLCF5))))
    
    PSCF1 = min(PLAR,NLCL)
    PSCF2 = min(PSAR,PSCL)
    PSCF3 = min(PSAR,ZECL)
    PSCF = compare(PSCF1,compare(PSCF2, PSCF3))
    
    ZECF1 = min(PSAR,NSCL)
    ZECF2 = min(ZEAR,PLCL)
    ZECF3 = min(ZEAR,PSCL)
    ZECF = compare(ZECF1,compare(ZECF2,ZECF3))

    NSCF1 = min(PSAR,NLCL)
    NSCF2 = min(ZEAR,ZECL)
    NSCF3 = min(ZEAR,NSCL)
    NSCF4 = min(NSAR,PLCL)
    NSCF5 = min(NSAR,PSCL)
    NSCF6 = min(NSAR,ZECL)
    NSCF7 = min(NLAR,PLCL)
    NSCF8 = min(NLAR,PSCL)
    NSCF9 = min(NLAR,ZECL)
    NSCF = compare(NSCF1,compare(NSCF2, compare(NSCF3, compare(NSCF4, compare(NSCF5, compare(NSCF6, compare(NSCF7, compare(NSCF8, NSCF9))))))))

    NLCF1 = min(NLAR, NLCL)
    NLCF2 = min(NLAR,NSCL)
    NLCF3 = min(NSAR, NLCL)
    NLCF4 = min(NSAR,NSCL)
    NLCF5 = min(ZEAR,NLCL)
    NLCF = compare(NLCF1,compare(NLCF2, compare(NLCF3, compare(NLCF4,NLCF5))))

    
    return PLCF, PSCF, ZECF, NSCF, NLCF

# De-fuzzyfication
def areaTR(mu, a,b,c):
    x1 = mu*(b-a) + a
    x2 = c - mu*(c-b)
    d1 = (c-a); d2 = x2-x1
    a = (1/2)*mu*(d1 + d2)
    return a # Returning area

def areaOL(mu, alpha, beta):
    xOL = beta -mu*(beta - alpha)
    return 1/2*mu*(beta+ xOL), beta/2

def areaOR(mu, alpha, beta):
    xOR = (beta - alpha)*mu + alpha
    aOR = (1/2)*mu*((270 - alpha) + (270 -xOR))
    return aOR, (270 - alpha)/2 + alpha

def defuzzyfication(PLCF, PSCF, ZECF, NSCF, NLCF):
    
    areaPL = 0; areaZE = 0; areaPS = 0; areaNS = 0; areaNL = 0;
    cPL = 0; cZE = 0; cPS = 0; cNS = 0; cNL = 0;

    if PLCF != 0:
        areaPL, cPL = areaOR(PLCF, 210, 270)
                
    if PSCF != 0:
        areaPS = areaTR(PSCF, 150, 210, 270)
        cPS = 210
    
    if ZECF != 0:
        areaZE = areaTR(ZECF, 90, 150, 210)
        cZE = 150
          
    if NSCF != 0:
        areaNS = areaTR(NSCF, 30, 90, 150)
        cNS = 90
        
    if NLCF !=0:
        areaNL, cNL = areaOL(NLCF, 30, 90)
        
    numerator = areaPL*cPL + areaPS*cPS + areaZE*cZE + areaNS*cNS + areaNL*cNL
    denominator = areaPL + areaPS + areaZE + areaNS + areaNL
    if denominator == 0:
        return -1
    else:
        crispOutput = numerator/denominator
        return crispOutput
    

def get_scores(Color, Area):

    # Getting fuzzy values for all the inputs for all the fuzzy sets
    NLCL,NSCL,ZECL,PSCL,PLCL = partition(Color)
    NLAR,NSAR,ZEAR,PSAR,PLAR = partition(Area)
    # NLRA,NSRA,ZERA,PSRA,PLRA = partition(RateArea)


    # Display the fuzzy values for all fuzzy sets
    outPut = [[NLCL,NSCL,ZECL,PSCL,PLCL],
            [NLAR,NSAR,ZEAR,PSAR,PLAR]]

    # print("The fuzzy values of the crisp inputs")
    # print(["NL","NS","ZE","PS", "PL"])
    # print(np.round(outPut,2))

    PLCF, PSCF, ZECF, NSCF, NLCF = rule(NLCL,NSCL,ZECL,PSCL,PLCL,NLAR,NSAR,ZEAR,PSAR,PLAR)

    # Display the fuzzy values for all rules
    # outPutRules = [[PLCF, PSCF, ZECF, NSCF, NLCF ]]
    # print("The fuzzy output: ")
    # print(["PLCF", "PSTC", "ZECF", "NSCF", "NLCF"])
    # print(np.round(outPutRules,2))

    crispOutputFinal = defuzzyfication(PLCF, PSCF, ZECF, NSCF, NLCF)
    # print(Color, Area, crispOutputFinal)
    print(crispOutputFinal)
    return crispOutputFinal

frames_path = 'D:\MTP\mtp-firecausedetection/shortcircuit-frames' #path to dir where frames are present
max_color_slope = 0
max_area_slope = 0
prev_color = 0
prev_area = 0

for fname in os.listdir(frames_path):
    img_path = os.path.join(frames_path, fname)
    # scores.append(get_scores(img_path))
    # print('__________',img_path, scores[-1])
    Color = cd.get_color(img_path)
    Area = cd.get_area(img_path)
    max_color_slope = max(abs(Color-prev_color), max_color_slope)
    max_area_slope = max(abs(Area-prev_area), max_area_slope)
    prev_area = Area
    prev_color = Color

print(max_color_slope, max_area_slope)
get_scores(min(300,max_color_slope), min(300,max_area_slope))
