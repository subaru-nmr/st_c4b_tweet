from logging.config import valid_ident
import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

st.caption('''資源循環シミュレーション機能の簡易版について説明します。
           簡易版は、インターネットを利用するすべてのユーザーに利用が許可されています。
           これは、プロフェッショナル向けの資源循環シミュレーション機能をより親しみやすく変化させたものです。
           そのため、一部のわかりにくい変数は変更不可能な値で固定されており、その結果、機能は制限されています。
           次に、資源循環シミュレーション機能について説明します。資源循環シミュレーションは、
           栽培施設のサイズを供給するエネルギー量から推定することで、設計支援を行います。
           入力する値は、地名・余熱量・CO2量が主なものですが、栽培施設に属するいくつかの
           パラメーターも必要となります。ソフトは、それらの入力された情報をもとに答えを導き出します。
           答えが返ってくるまでの待ち時間はほとんどなく、計算実行のボタンは省略されており、結果は入力値と連動するように変化します。''')



st.markdown('#### <簡易版>')
st.title('資源循環シミュレーション')

st.sidebar.selectbox('機能名：',('資源循環シミュレーション（簡易）','ダミー'),disabled=True)
container = st.sidebar.container()
region = container.selectbox('地名：',('千葉','滋賀','佐賀'))
dict_region_temp = {'千葉':-3,
                    '滋賀':-5,
                    '佐賀':1
                    }
dict_region_coordinate = {'千葉':[35.60472,140.12333],
                          '滋賀':[35.274361,136.259722],
                          '佐賀':[33.2635,130.300833]
                          }
region_value = dict_region_temp[region]
st.sidebar.write('最低気温：',region_value,'℃')

def heat_input():
    heat_supply = st.number_input('◆余熱量（kcal/h）：',min_value=0, max_value=99999999,value =800000,step=10000,help='供給熱量')
    st.write('入力値：',heat_supply,'(kcal/h)')
    st.write('入力値：',int(heat_supply*4.186/3600),'(kW)')
    return heat_supply
def co2_input():
    co2_supply = st.number_input('◆CO2量(kg/h)：',min_value=0, max_value=99999999,value =100,step=1,)
    st.write('入力値：',co2_supply,'(kg/h)')
    st.write('入力値：',int(co2_supply/0.044*8.314*273/101300),'(Nm3/h)')
    return co2_supply
def sv_input():
    set_value = st.number_input('◆設定温度℃：',min_value=5,max_value=33,value=18, help='5～33℃の間で決定してください。')
    return set_value
def curtain_input(dict_curtains):
    curtain = st.selectbox('◆内張り被覆材：',dict_curtains.keys(),index=1)
    st.write(f'選択したカーテン：{curtain}')
    k = dict_curtains[curtain]
    st.write('放熱係数：',k,'(kcal/㎡h℃)')
    return k
def choose_plant(dict_plants):
    plant = st.selectbox("作物の種類：",(dict_plants.keys()),disabled=False)
    light_coef = dict_plants[plant][0]
    ps_rate = dict_plants[plant][1]
    st.write('受光率：',light_coef)
    st.write('最大光合成速度：',ps_rate,'(kg/MJ)')
    return plant, light_coef, ps_rate
def house_spec_input():
    single_width = 7.2
    eaves = 6.0
    single_span =5.0
    a_ratio = 1.5
    st.selectbox('屋根の形状：',['三角屋根4.5寸','ダミー'],disabled=False)
    single_width = st.number_input('間口(m)：',value=single_width,disabled=False)
    eaves = st.number_input('軒高(m)：',value=eaves,disabled=False,step=0.1)
    single_span = st.number_input('スパン(m)：',value=single_span,disabled=False)
    a_ratio = st.number_input('敷地の形状：',value=a_ratio,disabled=False,step=0.1,min_value = 0.1,help='変更不可｜ハウスの幅と奥行きの割合です（幅÷奥行き）※棟数とスパン数で整数化されるため、結果は必ずしも一致するとは限りません。')
    return single_width, eaves, single_span, a_ratio
def heat_efficiency_input():
    heat_efficiency = 1.00
    heat_efficiency = st.slider('熱輸送効率：',value=heat_efficiency,min_value=0.0, max_value=1.0,disabled=False)
    if heat_efficiency == 0: heat_efficiency=0.01
    return heat_efficiency
def temp_dif(sv, rv):
    return sv-rv
def thermal_spec(roof_coef_1, roof_coef_2, theta, single_width, a_ratio, eaves, heat_supply, heat_efficiency):
    coef_2nd_order = round(roof_coef_1 * k * theta + 2.06 * theta -36,2)
    coef_1st_order = round(roof_coef_2 * a_ratio * theta / single_width + (a_ratio**0.5 + a_ratio**-0.5)* k * theta * 2 * eaves,2)
    intercept = -heat_supply * heat_efficiency
    root_area_mean = round((-coef_1st_order + (coef_1st_order**2 - 4 * coef_2nd_order * intercept)**0.5) / coef_2nd_order/2,2)
    thermal_area = round(root_area_mean ** 2,2)
    return coef_2nd_order, coef_1st_order, intercept, root_area_mean, thermal_area
def co2_spec(max_radiation, transparence, light_coef, ps_rate, co2_supply):
    co2_abs = round(max_radiation * transparence * light_coef * ps_rate * 3600 / 1000000,6)
    co2_area = round(co2_supply / co2_abs,2)
    return co2_abs, co2_area
def col4_output(theta, roof_coef_1, roof_coef_2):
    st.write('内外温度差：',theta,'（℃）')
    st.write('屋根形状係数１：',roof_coef_1,'[㎡/㎡]')
    st.write('屋根形状係数２：',roof_coef_2,'[㎡/棟]')
    return
def col50_output(coef_2nd_order,coef_1st_order,intercept, root_area_mean, thermal_area):
    st.write('方程式２次の係数：',coef_2nd_order,' ')
    st.write('方程式１次の係数：',coef_1st_order,' ')
    st.write('方程式切片：',intercept,' ')
    st.write('面積の平方根：',root_area_mean,'[m]')
    st.write('熱面積：',thermal_area,'[㎡]')
    return
def col51_output(max_radiation, transparence, light_coef, co2_abs, co2_area):
    st.write('最大日射量',max_radiation,'[W/m2]')
    st.write('光透過率',transparence)
    st.write('最大受光量',max_radiation * transparence * light_coef,'[W/m2]')
    st.write('CO2吸収速度',co2_abs,'[kg/h m2]')
    st.write('CO2面積',co2_area,'[m2]')
    return
def col6_output(root_area_mean, area, a_ratio, single_width, single_span):
    width_house = root_area_mean * a_ratio **0.5
    length_house = root_area_mean * a_ratio **-0.5
    number_roofs = int(round((width_house%single_width)/single_width, 0) + int(width_house/single_width))
    width_house = round(number_roofs * single_width,1)
    number_spans = int(area/width_house/single_span)
    length_house = round(number_spans *single_span,1)
    area = int(width_house * length_house)
    st.write('棟数：',number_roofs)
    st.write('スパン数：',number_spans)
    st.write('幅：',width_house,'[m]')
    st.write('奥行き：',length_house,'[m]')
def col7_output(area):
    st.metric('面積：',f'{area}[㎡]')
    st.write(f'{int(round(area/3.3,0))}[坪]')
dict_curtains = {'カーテンなし':5.2,
                    '1層（ラクソス）':3.6,
                    '1層（テンパ）':2.6,
                    '2層（テンパ＋ラクソス）':2.1
                    }
dict_plants = {'トマト':[0.85, 0.00278],
        'パプリカ':[0.80, 0.00231],
        'キュウリ':[0.80, 0.00299],
        'イチゴ':[0.45, 0.00215]
        }
roof_coef_1 = 1.17
roof_coef_2 = 14.4
max_radiation = 1000
transparence = 0.7

st.header('入力')
col1, col2, col3 = st.columns(3)
with col1:
    heat_supply = heat_input()
    co2_supply = co2_input()
with col2:
    set_value = sv_input()
    k = curtain_input(dict_curtains)
    plant, light_coef, ps_rate = choose_plant(dict_plants)
with col3:
    single_width, eaves, single_span, a_ratio = house_spec_input()
    heat_efficiency = heat_efficiency_input()


theta = temp_dif(set_value, region_value)
coef_2nd_order, coef_1st_order, intercept, root_area_mean, thermal_area = thermal_spec(roof_coef_1, roof_coef_2, theta, single_width, a_ratio, eaves, heat_supply, heat_efficiency)
co2_abs, co2_area = co2_spec(max_radiation, transparence, light_coef, ps_rate, co2_supply)
calculation_log = st.checkbox('途中の計算を表示する')
if calculation_log:
    st.markdown('# 演算')
    col4, col50, col51 = st.columns(3)
    with col4:
        col4_output(theta, roof_coef_1, roof_coef_2)
    with col50:
        col50_output(coef_2nd_order,coef_1st_order,intercept, root_area_mean, thermal_area)
    with col51:
        col51_output(max_radiation, transparence, light_coef, co2_abs, co2_area)
    st.text('ここに画像')
    
st.markdown('# 結果')
area = min(thermal_area, co2_area)
col6, col7 = st.columns(2)
with col6:
    col6_output(root_area_mean, area, a_ratio, single_width, single_span)
with col7:
    col7_output(area)

st.text("注意書き")
st.caption('''熱面積とCO2面積の小さい方が設計値となる。
           算定した面積をもとに年間の消費量をシミュレーションする。
           消費量をもとに取引量（熱、CO2）を算出する。
           エネルギーの単価を取引量に掛けて取引額を求める。
           単価には、供給額と市価で比較するため2値を入れることができる。
           最終的に熱取引額、CO2取引額、それらの合計額が求められる。''')

df=pd.DataFrame([dict_region_coordinate[region]],
         columns=['lat', 'lon'])
#st.table(df)

with container.expander("show map"):
    st.map(df, zoom=9)