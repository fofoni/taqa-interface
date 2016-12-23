function res = get_idx(SINAIS, sinal, teste, parametro)

res = [];

for i = 1:length(SINAIS)
    if strcmp(sinal,'') || strcmp(SINAIS(i).sinal, sinal)
    if strcmp(teste,'') || strcmp(SINAIS(i).teste, teste)
    if strcmp(parametro,'') || strcmp(SINAIS(i).parametro, parametro)
        res = [res i]; %#ok<AGROW>
    end
    end
    end
end
