import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("למה T0 מזיז רק את הקו הכחול?")

# סליידרים עם השפעה ויזואלית חזקה
T0 = st.sidebar.slider("טמפרטורת הזנה (T0)", 200, 400, 300)
UA = st.sidebar.slider("מקדם קירור (UA)", 0.0, 5.0, 1.0)
Ta = st.sidebar.slider("טמפרטורת קירור (Ta)", 250, 350, 290)

T_range = np.linspace(200, 600, 500)

# פרמטרים כימיים קבועים
k0 = 1e10
Ea_R = 8000
dH = -80000
V_tau = 10 # ספיקה

def sim(T):
    # כימיה (אדום) - לא תלוי ב-T0
    k = k0 * np.exp(-Ea_R / T)
    X = (20 * k) / (1 + 20 * k)
    Qgen = (-dH) * V_tau * X
    
    # פיזיקה (כחול) - כאן T0 חייב להשפיע!
    # החלק הראשון הוא החום שיוצא עם הזרם. אם T0 עולה, הביטוי (T-T0) קטן -> פחות חום מתפנה
    Q_flow = V_tau * 500 * (T - T0) 
    Q_cool = UA * 500 * (T - Ta)
    Qrem = Q_flow + Q_cool
    return Qgen, Qrem

Qgen_vals, Qrem_vals = sim(T_range)

fig = go.Figure()
fig.add_trace(go.Scatter(x=T_range, y=Qgen_vals, name="ייצור חום (כימיה)", line=dict(color='red')))
fig.add_trace(go.Scatter(x=T_range, y=Qrem_vals, name="פינוי חום (פיזיקה)", line=dict(color='blue')))

fig.update_layout(xaxis=dict(range=[200, 600]), yaxis=dict(range=[0, 1e7]), title=f"מצב נוכחי: T0 = {T0}K")
st.plotly_chart(fig)

st.write("""
### מה לבדוק עכשיו?
תזיזי את הסליידר של **T0** ימינה ושמאלה. 
* שימי לב איך הקו הכחול **מחליק** לאורך ציר ה-X. 
* ב-T0 נמוך (הזנה קרה), הקו הכחול גבוה מאוד, וקשה לכור "להידלק". 
* ב-T0 גבוה (הזנה חמה), הקו הכחול יורד, ופתאום נוצרות נקודות חיתוך חדשות עם ה-S האדומה.
""")