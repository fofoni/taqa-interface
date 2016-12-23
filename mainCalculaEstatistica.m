clear all
close all
clc

run('resultados.m'); % Cria as variáveis necessárias no workspace

if exist('mapeamento.mat', 'file') % PAQM mapeado na escala MOS
    load mapeamento.mat
    
    notas_paqm = notasPreditas';
else % PAQM não mapeado
    [notas,~,~] = xlsread('notas_paqm');

    notas_paqm = zeros(1, length(SINAIS));
    idx_paqm = 1;
    
    matriz_notas_ruido = notas(:,2:4);
    matriz_notas_codec = notas(:,5:7);
    vetor_notas_codec_4k = notas(:,1);
    
    for i = 1:size(matriz_notas_ruido, 1)
        for j = 1:size(matriz_notas_ruido, 2)
            if ~isnan(matriz_notas_ruido(i,j))
                notas_paqm(idx_paqm) = matriz_notas_ruido(i,j);
                idx_paqm = idx_paqm + 1;
            end
        end
    end
    
    for i = 1:size(matriz_notas_codec, 1)
        for j = 1:size(matriz_notas_codec, 2)
            if ~((i == 1 && j == 2) || (i == size(matriz_notas_codec, 1) && j == 2)) % Não conta Berimbau_128k nem Chopin_128k
                notas_paqm(idx_paqm) = matriz_notas_codec(i,j);
                idx_paqm = idx_paqm + 1;
            end
        end
    end
    
    for i = 1:length(vetor_notas_codec_4k)
        notas_paqm(idx_paqm) = vetor_notas_codec_4k(i);
        idx_paqm = idx_paqm + 1;
    end
end

nomes_participantes = NOMES;

num_testes_ruido = 0;
num_testes_codec = 0;
num_testes_codec_4k = 0;

for i = 1:length(SINAIS)
    switch SINAIS(i).teste
        case 'SNR'
            num_testes_ruido = num_testes_ruido + 1;
        case 'CODEC'
            num_testes_codec = num_testes_codec + 1;
        case 'CODEC4KHZ'
            num_testes_codec_4k = num_testes_codec_4k + 1;
    end
end

idx_coluna_inicial_testes_ruido = 1;
idx_coluna_final_testes_ruido = num_testes_ruido;
idx_coluna_inicial_testes_codec = idx_coluna_final_testes_ruido + 1;
idx_coluna_final_testes_codec = idx_coluna_inicial_testes_codec + num_testes_codec - 1;
idx_coluna_inicial_testes_codec_4k = idx_coluna_final_testes_codec + 1;
idx_coluna_final_testes_codec_4k = idx_coluna_inicial_testes_codec_4k + num_testes_codec_4k - 1;

dados = [NOTAS; notas_paqm];

for i = 1:size(dados, 1) - 1 % Itera por cada pessoa; última linha de 'dados' é PAQM e, por isso, itera só até size(dados, 1) - 1

    num_testes_ruido_validos = num_testes_ruido;
    num_testes_codec_validos = num_testes_codec;
    num_testes_codec_4k_validos = num_testes_codec_4k;

    notas_pessoa = dados(i, :);
    idx_notas_invalidas = find(notas_pessoa == -Inf);
    idx_notas_validas = find(notas_pessoa > 0);

    if ~isempty(idx_notas_invalidas) % Conta a quantidade de resultados válidos por classe de teste (SNR, CODEC ou CODEC4KHZ)
        for j = 1:length(idx_notas_invalidas)
                if (idx_notas_invalidas(j) >= idx_coluna_inicial_testes_ruido && idx_notas_invalidas(j) <= idx_coluna_final_testes_ruido)
                    num_testes_ruido_validos = num_testes_ruido_validos - 1;
                else if (idx_notas_invalidas(j) >= idx_coluna_inicial_testes_codec && idx_notas_invalidas(j) <= idx_coluna_final_testes_codec)
                    num_testes_codec_validos = num_testes_codec_validos - 1;
                    else if (idx_notas_invalidas(j) >= idx_coluna_inicial_testes_codec_4k && idx_notas_invalidas(j) <= idx_coluna_final_testes_codec_4k)
                    num_testes_codec_4k_validos = num_testes_codec_4k_validos - 1;
                        end
                    end
                end
        end
    end

    notas_validas_pessoa = notas_pessoa(idx_notas_validas);
    notas_validas_paqm = notas_paqm(idx_notas_validas);

    id = strcat(num2str(num_testes_ruido_validos > 0), num2str(num_testes_codec_validos > 0), num2str(num_testes_codec_4k_validos > 0));

    figure

    switch id
        case '001' % Só fez o teste do codec 4k
            idx_coluna_inicial_testes_codec_4k_validos = 1;
            idx_coluna_final_testes_codec_4k_validos = num_testes_codec_4k_validos;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), 'k+');

            legend('CODEC4K')
            
        case '010' % Só fez o teste do codec
            idx_coluna_inicial_testes_codec_validos = 1;
            idx_coluna_final_testes_codec_validos = num_testes_codec_validos;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), 'rx');

            legend('CODEC')
            
        case '100' % Só fez o teste o ruido
            idx_coluna_inicial_testes_ruido_validos = 1;
            idx_coluna_final_testes_ruido_validos = num_testes_ruido_validos;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), notas_validas_paqm(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), 'bo');

            legend('SNR')
            
        case '110' % Fez os testes de ruido e codec
            idx_coluna_inicial_testes_ruido_validos = 1;
            idx_coluna_final_testes_ruido_validos = num_testes_ruido_validos;
            idx_coluna_inicial_testes_codec_validos = idx_coluna_final_testes_ruido_validos + 1;
            idx_coluna_final_testes_codec_validos = idx_coluna_inicial_testes_codec_validos + num_testes_codec_validos - 1;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), notas_validas_paqm(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), 'bo');
            hold on
            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), 'rx');
            hold off
            
            legend('SNR', 'CODEC')

        case '101' % Fez os testes de ruido e codec 4k
            idx_coluna_inicial_testes_ruido_validos = 1;
            idx_coluna_final_testes_ruido_validos = num_testes_ruido_validos;
            idx_coluna_inicial_testes_codec_4k_validos = idx_coluna_final_testes_ruido_validos + 1;
            idx_coluna_final_testes_codec_4k_validos = idx_coluna_inicial_testes_codec_4k_validos + num_testes_codec_4k_validos - 1;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), notas_validas_paqm(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), 'bo');
            hold on
            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), 'k+');
            hold off
            
            legend('SNR', 'CODEC4K')

        case '011' % Fez os testes de codec e codec 4k
            idx_coluna_inicial_testes_codec_validos = 1;
            idx_coluna_final_testes_codec_validos = num_testes_codec_validos;
            idx_coluna_inicial_testes_codec_4k_validos = idx_coluna_final_testes_codec_validos + 1;
            idx_coluna_final_testes_codec_4k_validos = idx_coluna_inicial_testes_codec_4k_validos + num_testes_codec_4k_validos - 1;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), 'rx');
            hold on
            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), 'k+');
            hold off
            
            legend('CODEC', 'CODEC4K')

        case '111' % Fez todos os testes
            idx_coluna_inicial_testes_ruido_validos = 1;
            idx_coluna_final_testes_ruido_validos = num_testes_ruido_validos;
            idx_coluna_inicial_testes_codec_validos = idx_coluna_final_testes_ruido_validos + 1;
            idx_coluna_final_testes_codec_validos = idx_coluna_inicial_testes_codec_validos + num_testes_codec_validos - 1;
            idx_coluna_inicial_testes_codec_4k_validos = idx_coluna_final_testes_codec_validos + 1;
            idx_coluna_final_testes_codec_4k_validos = idx_coluna_inicial_testes_codec_4k_validos + num_testes_codec_4k_validos - 1;

            plot(notas_validas_pessoa(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), notas_validas_paqm(idx_coluna_inicial_testes_ruido_validos:idx_coluna_final_testes_ruido_validos), 'bo');
            hold on
            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_validos:idx_coluna_final_testes_codec_validos), 'rx');
            plot(notas_validas_pessoa(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), notas_validas_paqm(idx_coluna_inicial_testes_codec_4k_validos:idx_coluna_final_testes_codec_4k_validos), 'k+');
            hold off
            
            legend('SNR', 'CODEC', 'CODEC4K')

    end


%     coef_corr = mean(((notas_validas_pessoa - mean(notas_validas_pessoa)) .* (notas_validas_paqm - mean(notas_validas_paqm))))/(std(notas_validas_pessoa)*std(notas_validas_paqm));
    R = corrcoef(notas_validas_pessoa', notas_validas_paqm');
    coef_corr = R(1,2); % Coeficiente de correlação
%     [coef_corr coef_corr_2(1,2)]

    title(strcat(nomes_participantes(i), ' (\rho = ', num2str(coef_corr*100), ' %)'));
    xlabel('MOS medido');
    ylabel('MOS previsto');
    set(gca, 'XLim', [1 5], 'YLim', [1 5]);
    
%     keyboard

end

figure

notas_ruido = dados(1:end-1,idx_coluna_inicial_testes_ruido:idx_coluna_final_testes_ruido);
notas_codec = dados(1:end-1,idx_coluna_inicial_testes_codec:idx_coluna_final_testes_codec);
notas_codec_4k = dados(1:end-1,idx_coluna_inicial_testes_codec_4k:idx_coluna_final_testes_codec_4k);

notas_paqm_ruido = dados(end,idx_coluna_inicial_testes_ruido:idx_coluna_final_testes_ruido);
notas_paqm_codec = dados(end,idx_coluna_inicial_testes_codec:idx_coluna_final_testes_codec);
notas_paqm_codec_4k = dados(end,idx_coluna_inicial_testes_codec_4k:idx_coluna_final_testes_codec_4k);

notas_medias_validas_ruido = zeros(1,size(notas_ruido, 2));
notas_medias_validas_codec = zeros(1,size(notas_codec, 2));
notas_medias_validas_codec_4k = zeros(1,size(notas_codec_4k, 2));

for i = 1:size(notas_ruido, 2)
    notas_validas_ruido = notas_ruido(notas_ruido(:,i)>0, i);
    notas_medias_validas_ruido(i) = mean(notas_validas_ruido);
end

for i = 1:size(notas_codec, 2)
    notas_validas_codec = notas_codec(notas_codec(:,i)>0, i);
    notas_medias_validas_codec(i) = mean(notas_validas_codec);
end

for i = 1:size(notas_codec_4k, 2)
    notas_validas_codec_4k = notas_codec_4k(notas_codec_4k(:,i)>0, i);
    notas_medias_validas_codec_4k(i) = mean(notas_validas_codec_4k);
end

notas_medias_validas = [notas_medias_validas_ruido notas_medias_validas_codec notas_medias_validas_codec_4k];
notas_paqm = [notas_paqm_ruido notas_paqm_codec notas_paqm_codec_4k];
coef_corr = mean(((notas_medias_validas - mean(notas_medias_validas)) .* (notas_paqm - mean(notas_paqm))))/(std(notas_medias_validas)*std(notas_paqm));

plot(notas_medias_validas_ruido, notas_paqm_ruido, 'bo');
hold on
plot(notas_medias_validas_codec, notas_paqm_codec, 'rx');
plot(notas_medias_validas_codec_4k, notas_paqm_codec_4k, 'k+');
hold off

legend('SNR', 'CODEC', 'CODEC4K');
title(strcat('Geral (\rho = ', num2str(coef_corr*100), ' %)'))
xlabel('MOS medido')
ylabel('MOS previsto')
set(gca, 'XLim', [1 5], 'YLim', [1 5])
