library("dplyr")
# need this to show russian characters
Sys.setlocale("LC_CTYPE", "ru_RU")

# prepare data
money = read.csv('../data/money.csv',sep=',', stringsAsFactors=FALSE, encoding = "UTF-8")
money = as_data_frame(money) %>%
  filter(counted == 'True', receiver_username != 'pioner_bankir') %>%
  mutate(creation_timestamp = as.POSIXct(creation_timestamp, format = "%d.%m.%Y %H:%M")) %>%
  mutate(creation_day = as.numeric(format(creation_timestamp,"%d")),creation_weekday =format(creation_timestamp,"%A"), creation_hour = as.numeric(format(creation_timestamp,"%H"))) %>%
  mutate(creation_part_of_day = floor(creation_hour/6)) %>%
  arrange(creation_timestamp) 


counters = read.csv('../data/counters.csv',sep=',', stringsAsFactors=FALSE, encoding = "UTF-8")
counters = as_data_frame(counters) %>%
  filter(counted == 'True', receiver_username != 'pioner_bankir' ) %>%
  mutate(creation_timestamp = as.POSIXct(creation_timestamp, format = "%d.%m.%Y %H:%M")) %>%
  mutate(creation_day = as.numeric(format(creation_timestamp,"%d")),creation_weekday =format(creation_timestamp,"%W"), creation_hour = as.numeric(format(creation_timestamp,"%H"))) %>%
  mutate(creation_part_of_day = floor(creation_hour/6)) %>%
  arrange(creation_timestamp)

#


###feature extraction
 ##money
 # basic info
time_money_features = money %>%
  group_by(creation_day) %>%
  summarise(creation_weekday = first(creation_weekday),
            income_money = sum(value[value>0]),
            outcome_money = sum(value[value<0]),
            total_money_change = sum(value)) %>%
  mutate(total_money_on_day_end = cumsum(total_money_change)) %>%
  arrange(creation_day)

money_features = money %>%
  group_by(creation_day, type_readable_name) %>%
  summarise(value = sum(value))
money_features_table = as.data.frame.matrix(xtabs(value~creation_day+type_readable_name, data= money_features))

money_general_features = money %>%
  group_by(creation_day, type_group_general) %>%
  summarise(value = sum(value))
money_general_features_table = as.data.frame.matrix(xtabs(value~creation_day+type_group_general, data= money_general_features))
colnames(money_general_features_table) <- paste("Все", colnames(money_general_features_table), sep = " ")


### Counters feature extraction
counter_features = counters %>%
  group_by(creation_day, type_readable_name) %>%
  summarise(value = sum(value))
counter_features_table = as.data.frame.matrix(xtabs(value~creation_day+type_readable_name, data= counter_features))
colnames(counter_features_table) <- paste("Счетчики", colnames(counter_features_table), sep = " ")


temprow <- matrix(c(rep.int(0,length(counter_features_table))),nrow=1,ncol=length(counter_features_table))
# make it a data.frame and give cols the same names as data
newrow <- data.frame(temprow)
colnames(newrow) <- colnames(counter_features_table)
# rbind the empty row to data
counter_features_table <- bind_rows(newrow,counter_features_table,newrow)

time_features = bind_cols(time_money_features, money_features_table, money_general_features_table, counter_features_table)

write.csv(time_features, '../data/time_features.csv')

