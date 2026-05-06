import streamlit as st

st.title("ReadMe")


name = st.session_state.get('name', 'Gast')

st.subheader(f"Willkommen, {name}!")

st.write("""
Diese App ermöglicht Lehrpersonen, Texte einfach und strukturiert bereitzustellen. Schülerinnen und Schüler können die veröffentlichten Inhalte lesen und ihr Verständnis anschliessend durch ein integriertes Quiz überprüfen.
""")

"""

## Diese App wurde von folgenden Personen entwickelt:

- Bal       Jasleen     (baljas01@students.zhaw.ch) 
- Britone   Luana       (birtolua@students.zhaw.ch)
- Suter     Kaj         (suterkaj@students.zhaw.ch)
- Trüb      Larissa     (trueblar@students.zhaw.ch)



Das gerüst für diese App wurde freundlicherweise bereitgestellt durch:

- Samuel    Wehrli      (wehs@zhaw.ch)
"""
