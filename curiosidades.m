clear all %#ok<CLSCR>
resultados

NOTAS(NOTAS == -Inf) = NaN;

figure;
hist(NOTAS(:),linspace(1,5,101));
xlim([0.98  5.02]);
xlabel('MOS');

tempo_de_transicao = 3/60;

figure;
hold on;
total = (25.01 + 22.00 + 14.1 + 21.2 + 12.7 + 14.25 + 13)*2*3/60;
total = total + 21*tempo_de_transicao;
plot(total*1.0*[1 1], [0 6], 'k');
plot(total*1.5*[1 1], [0 6], 'k');
plot(total*2.0*[1 1], [0 6], 'k');
plot(total*2.5*[1 1], [0 6], 'k');
hist(TEMPOS(:,1));
xlabel('Tempo (min)');
xlim([4 38]);

figure;
hold on;
total = (25.01 + 22.00 + 14.1 + 21.2 + 12.7 + 14.25 + 16.16 + 13)*2*3/60;
total = total + 24*tempo_de_transicao;
plot(total*1.0*[1 1], [0 6], 'k');
plot(total*1.5*[1 1], [0 6], 'k');
plot(total*2.0*[1 1], [0 6], 'k');
plot(total*2.5*[1 1], [0 6], 'k');
hist(TEMPOS(:,2));
xlabel('Tempo (min)');
xlim([4 38]);

figure;
hold on;
total = (25.01 + 22.00 + 14.1 + 21.2 + 12.7 + 14.25 + 16.16)*2/60;
total = total + 7*tempo_de_transicao;
plot(total*1.0*[1 1], [0 6], 'k');
plot(total*1.5*[1 1], [0 6], 'k');
plot(total*2.0*[1 1], [0 6], 'k');
plot(total*2.5*[1 1], [0 6], 'k');
hist(TEMPOS(:,3));
xlabel('Tempo (min)');
xlim([4 38]);
