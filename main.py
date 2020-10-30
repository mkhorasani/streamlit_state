import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from streamlit.report_thread import get_report_ctx

def get_session():
    session_id = get_report_ctx().session_id
    return session_id

def write_state(column,value,engine,session_id):
    engine.execute("UPDATE %s SET %s='%s'" % (session_id,column,value))

def write_state_df(df,session_id):
    df.to_sql('%s' % (session_id),engine,index=False,if_exists='replace',chunksize=1000)

def read_state(column,engine,session_id):
    query_return = engine.execute("SELECT %s FROM %s" % (column,session_id))
    query_return = query_return.first()[0]
    return query_return

def read_state_df(session_id):
    try:
        df = pd.read_sql_table(session_id,con=engine)
    except:
        df = pd.DataFrame([])
    return df

if __name__ == '__main__':

    #Creating PostgreSQL client
    engine = create_engine('postgresql://postgres:<password>@localhost:5432/postgres')

    #Getting session ID
    session_id = get_session()
    session_id = session_id.replace('-','_')
    session_id = '_id_' + session_id

    #Creating session state tables
    engine.execute("CREATE TABLE IF NOT EXISTS %s (size text)" % (session_id))
    len_table =  engine.execute("SELECT COUNT(*) FROM %s" % (session_id));
    len_table = len_table.first()[0]

    if len_table == 0:
        engine.execute("INSERT INTO %s (size) VALUES ('1')" % (session_id));
    
    #Creating pages
    page = st.sidebar.selectbox('Select page:',('Page One','Page Two'))

    if page == 'Page One':
        st.write('Hello world')
        
    elif page == 'Page Two':
        size = st.text_input('Matrix size',read_state('size',engine,session_id))
        write_state('size',size,engine,session_id)
        size = int(read_state('size',engine,session_id))

        if st.button('Click'):
            data = [[0 for (size) in range((size))] for y in range((size))]
            df = pd.DataFrame(data)
            write_state_df(df,session_id + '_df')

        if read_state_df(session_id + '_df').empty is False:
            df = read_state_df(session_id + '_df')
            st.write(df)
    
