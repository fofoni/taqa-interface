function [t,df] = significancia(x,y)

d = mean(y-x, 'omitnan');
s2 = var(y-x, 'omitnan');
n = sum(~isnan(y-x));
df = n-1;
t = d / sqrt(s2/n);
