import panel as pn
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd

df = pd.read_csv('participants_information.csv', encoding='utf-8', encoding_errors='replace')

participant_count_card = pn.indicators.Number(name='n_participants', value = 329, colors = [(100, 'black')])
teams_count_card = pn.indicators.Number(name='n_teams', value = 45, colors = [(100, 'black')])
schools_count_card = pn.indicators.Number(name='n_schools', value = 4, colors = [(100, 'black')])
no_team_count_card = pn.indicators.Number(name='n_particip_no_team', value = 100, colors = [(100, 'black')])
solo_participants_count_card = pn.indicators.Number(name='n_solo', value = 51, colors = [(100, 'black')])

df = pd.read_csv('participants_information.csv')


df['RegisterTime(UTC0)'] = pd.to_datetime(df["RegisterTime(UTC0)"])
df['register_date'] = df['RegisterTime(UTC0)'].apply(lambda x: datetime.strftime(x, '%Y-%m-%d'))



cards_column = pn.Column(participant_count_card,
                         teams_count_card,
                         schools_count_card,
                         no_team_count_card,
                         solo_participants_count_card)


def plot_registration_per_day():
    counts = df.groupby('register_date')['Email'].count()
    plt.figure(figsize=(6, 4))
    plt.plot(counts.index, counts.values, marker='o', color='orange')
    plt.title("Registrations Per Day")
    plt.xlabel("Date")
    plt.ylabel("Number of Registrations")
    plt.grid(True)
    return plt.gcf()

join_per_day = pn.pane.Matplotlib(plot_registration_per_day())

template = pn.template.GoldenTemplate(title = 'test')
template.main.append(cards_column)
template.main.append(join_per_day)

template.servable()


