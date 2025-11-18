def validar_campos(data, campos):
    for c in campos:
        assert c in data
