from statistics import median

def weighted_quantile(values,fraction):
    sorted_values=sorted(values)
    position=(len(values)-1)*fraction
    low=int(position)
    high=min(low+1,len(values)-1)
    return sorted_values[low] + (position-low)*(sorted_values[high]-sorted_values[low])

def describe(values):
    if not values:
        return {"n":0,"median":None,"mad":None,"p90":None,"values":[]}
    middle=median(values)
    return {"n":len(values),"median":round(middle,3),
            "mad":round(median(abs(value-middle) for value in values),3),
            "p90":round(weighted_quantile(values,.9),3),"values":sorted(values)}
