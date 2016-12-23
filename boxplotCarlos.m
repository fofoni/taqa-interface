%Rodando script do Fonini
resultados;

notas = NOTAS;
sinais = SINAIS;

notas(notas == -Inf) = NaN;
[~, I] = sort(nanmean(notas));
sinais = sinais(I);
notas = notas(:,I);
boxplot(notas)
axis([0,45, 0.9, 5.1]);
xlabel({ 'Número do Sinal', '(olhar tabela de correspondência)'});
ylabel('Nota na escala MOS');
title('Notas para cada sinal de teste');


nomeSinal = {};
parametros = {};
tipoTeste = {};
label = {};
notasColuna = [];

for i = 1:length(sinais)
    notasTeste = notas(:,i);
    notasTeste = notasTeste(~isnan(notasTeste));
    a = cellstr(repmat(sinais(i).sinal, length(notasTeste),1));
    b = cellstr(repmat(sinais(i).teste, length(notasTeste),1));
    c = cellstr(repmat(sinais(i).parametro, length(notasTeste),1));
    
    nomeSinal = vertcat(nomeSinal , a);
    tipoTeste = vertcat(tipoTeste, b);
    parametros = vertcat(parametros, c);
    
    notasColuna = [notasColuna; notasTeste];
    label = vertcat(label, strcat(sinais(i).sinal,'_', sinais(i).teste,'_', sinais(i).parametro)); 
end

%Sinal = strcat(nomeSinal,'_', tipoTeste,'_', parametros);
%figure;
%boxplot(notasColuna, Sinal);
%figure;
%boxplot(notasColuna, parametros);
figure;
for i= 1: length(tipoTeste)
    teste_temp = tipoTeste{i};
    if strcmp(teste_temp, 'CODEC4KHZ')
        parametros{i} = 'CODEC 4K';
    end
end
boxplot(notasColuna, parametros);
xlabel('Parâmetro testado');
ylabel('Nota na escala MOS');
title('Notas por parâmetro testado');
figure;
boxplot(notasColuna, parametros, 'GroupOrder', {'20dB', '35dB', '50dB', '64k', '128k', '320k', 'CODEC 4K'});
xlabel('Parâmetro testado');
ylabel('Nota na escala MOS');
title('Notas por parâmetro testado'); 
