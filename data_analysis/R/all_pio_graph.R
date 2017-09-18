data = read.csv('../data/money.csv',sep=',', stringsAsFactors=FALSE)
data = as_data_frame(data)
data = mutate(data,creation_timestamp = as.POSIXct(creation_timestamp, format = "%d.%m.%Y %H:%M"))
Encoding(colnames(data)) <- "UTF-8"


real_money = data %>%
  filter(counted == 'True') %>%
  arrange(creation_timestamp) %>%
  select(receiver_username, value, timestamp = creation_timestamp)

grouped_m = group_by(real_money,receiver_username)
balances_flow = mutate(grouped_m, bal = cumsum(value))


# plotting
plot = ggplot(balances_flow,aes(x = timestamp,y = bal, group = receiver_username )) + 
  geom_line(size = .2,alpha = .3, col = 'black') + 
  geom_point(size = .2,alpha = .3, col = 'black') + 
  geom_hline(yintercept = 0, col = 'red') + 
  
  scale_x_datetime(date_breaks="1 days", 
                   labels = function(x) strftime(x,format = "%d"),
                   name = 'Day Of August') + 
  scale_y_continuous(name = 'Pioner Balance',
                     breaks = seq(-150,1100,50)) + 
  theme_bw()
plot
