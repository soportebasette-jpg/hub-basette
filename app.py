# Pestañas de Visualización
        tab_r, tab_e, tab_t = st.tabs(["🏆 RANKING", "⚡ ENERGÍA", "📱 TELCO"])

        with tab_r:
            if not de.empty or not dt.empty:
                re = de.groupby('Comercial')[['V_Luz', 'V_Gas']].sum() if not de.empty else pd.DataFrame()
                rt = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum() if not dt.empty else pd.DataFrame()
                
                rank = pd.concat([re, rt], axis=1).fillna(0)
                rank['TOTAL'] = rank.sum(axis=1)
                rank = rank.sort_values('TOTAL', ascending=False)

                if not rank.empty:
                    ganador = rank.index[0]
                    total_ganador = int(rank.iloc[0]['TOTAL'])
                    st.markdown(f"""<div class="winner-card">👑 EL NÚMERO 1: {ganador.upper()} ({total_ganador} VENTAS) 👑</div>""", unsafe_allow_html=True)
                    
                    rank_visual = rank.reset_index()
                    st.table(rank_visual.style.format(precision=0))
            else:
                st.warning("No hay datos disponibles para los filtros seleccionados.")

        with tab_e:
            if not de.empty:
                col_e1, col_e2 = st.columns([1, 1.2])
                with col_e1:
                    # Usamos .get() para evitar que la app explote si no existe la columna
                    col_nom = 'Comercializadora' if 'Comercializadora' in de.columns else de.columns[0]
                    fig_e = px.pie(de, values='Total_Ene', names=col_nom, hole=0.5, title="Cuota de Energía")
                    st.plotly_chart(fig_e, use_container_width=True)
                with col_e2:
                    ventas_e = de.groupby('Comercial')['Total_Ene'].sum().reset_index().sort_values('Total_Ene')
                    fig_eb = px.bar(ventas_e, x='Total_Ene', y='Comercial', orientation='h', text_auto=True, title="Ventas Energía")
                    st.plotly_chart(fig_eb, use_container_width=True)
            else:
                st.info("No hay datos de Energía para mostrar.")

        with tab_t:
            if not dt.empty:
                col_t1, col_t2 = st.columns([1, 1.2])
                with col_t1:
                    col_op = 'Operadora' if 'Operadora' in dt.columns else dt.columns[0]
                    fig_t = px.pie(dt, values='Total_Tel', names=col_op, hole=0.5, title="Cuota de Telco")
                    st.plotly_chart(fig_t, use_container_width=True)
                with col_t2:
                    mix_t = dt.groupby('Comercial')[['V_Fibra', 'V_Móvil']].sum().reset_index()
                    fig_tb = px.bar(mix_t, x='Comercial', y=['V_Fibra', 'V_Móvil'], barmode='group', title="Mix de Telco")
                    st.plotly_chart(fig_tb, use_container_width=True)
            else:
                st.info("No hay datos de Telco para mostrar.")