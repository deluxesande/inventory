crazy_tuple = (["x","y"],)
crazy_tuple[0] = crazy_tuple[0].__iadd__(["z"])
print(crazy_tuple[0])