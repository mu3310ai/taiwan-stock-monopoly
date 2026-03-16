import streamlit as st
import random
import time
import json 
import plotly.graph_objects as go 
import pandas as pd 

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

# ==========================================
# [1] 設定與資料庫區塊 (Data & Config)
# ==========================================
AUDIO_URLS = {
    "bgm": "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",      
    "dice": "https://cdn.pixabay.com/audio/2022/03/15/audio_145973fb39.mp3",     
    "footstep": "https://cdn.pixabay.com/audio/2022/03/15/audio_73133b3b6c.mp3", 
    "tada": "https://cdn.pixabay.com/audio/2021/08/04/audio_12b0c7443c.mp3",     
    "fail": "https://cdn.pixabay.com/audio/2021/08/04/audio_c6ccf3232f.mp3",     
    "cash": "https://cdn.pixabay.com/audio/2021/08/09/audio_415f9ce02a.mp3"      
}

QUIZ_BANK = [
    {"q": "「雞蛋不要放在同一個籃子裡」是指什麼？", "opts": ["A. 分散風險", "B. 集中獲利", "C. 節省手續費"], "ans": 0, "exp": "分散投資可避免單一公司倒閉造成血本無歸。"},
    {"q": "「通貨膨脹」加劇時，你的現金會怎樣？", "opts": ["A. 價值變薄", "B. 價值變厚", "C. 毫無影響"], "ans": 0, "exp": "通膨代表物價上漲，現金的購買力會跟著縮水。"},
    {"q": "什麼是「ETF」？", "opts": ["A. 危險飆股", "B. 買進一籃子股票的組合包", "C. 定存方案"], "ans": 1, "exp": "ETF 就像綜合福袋，買一張等於買幾十家好公司。"},
    {"q": "大家樂觀瘋狂買股票的市場稱為？", "opts": ["A. 熊市", "B. 豬市", "C. 牛市"], "ans": 2, "exp": "牛角往上頂代表上漲；熊爪往下拍代表下跌。"},
    {"q": "利息也能生利息的強大力量是？", "opts": ["A. 單利", "B. 複利", "C. 高利貸"], "ans": 1, "exp": "複利像滾雪球，時間越久財富增長越驚人。"},
    {"q": "公司把利潤發放給股東的錢稱為？", "opts": ["A. 手續費", "B. 股息", "C. 資本利得"], "ans": 1, "exp": "長期持有好公司，不賣掉也能領被動收入股息。"},
    {"q": "台積電被稱為「權值股」代表？", "opts": ["A. 市值大，極度影響大盤", "B. 新創公司", "C. 快破產了"], "ans": 0, "exp": "權值股就像班上第一名，成績稍微退步就會拉低全班平均。"},
    {"q": "哪種行為才叫「投資」？", "opts": ["A. 買新手機", "B. 錢藏床底", "C. 買潛力資產(股票/房產)"], "ans": 2, "exp": "買進未來會增值或幫你賺錢的東西，才叫投資！"}
]

CHANCE_CARDS = [
    ("【神秘包裹】獲得高科技產品，內含遙控骰子！", "item", "🎲遙控骰子"), ("【貴人相助】遇到貴人指點迷津，獲得免死金牌！", "item", "🛡️免死金牌"),
    ("【交通部活動】抽中免費票券，獲得高鐵卡！", "item", "🚀高鐵卡"), ("【外資大舉買超】台股大漲，獲利 50萬！", "money", 500000),
    ("【AI 伺服器爆單】供應鏈齊揚，獲得 80萬！", "money", 800000), ("【政府普發現金】振興經濟，獲得 20萬！", "money", 200000),
    ("【財報超級亮眼】超乎預期，獲利 60萬！", "money", 600000), ("【降息預期落空】熱錢流出，損失 30萬！", "money", -300000),
    ("【地緣政治緊張】恐慌跳水，損失 40萬！", "money", -400000), ("【胖手指下錯單】高檔買進，損失 20萬！", "money", -200000),
    ("【內線交易調查】配合檢調約談，暫停行動一回合！", "skip", 1), ("【科技大廠建廠】帶動房地產，獲得 40萬！", "money", 400000),
    ("【申購新股中籤】幸運兒是你！現賺 70萬！", "money", 700000), ("【刮刮樂中頭獎】運氣爆棚，現賺 200萬！", "money", 2000000)
]

FATE_CARDS = [
    ("【街頭奇遇】撿到奇怪寶箱，獲得遙控骰子！", "item", "🎲遙控骰子"), ("【防身符】廟宇求得平安符，獲得免死金牌！", "item", "🛡️免死金牌"),
    ("【黑市交易】透過特殊管道，獲得查稅卡！", "item", "💳查稅卡"), ("【拘票送達】涉嫌內線交易，入獄停 2 回合！", "jail", 0),
    ("【生日快樂】大家幫你慶生，向全員收 20萬！", "collect_all", 200000), ("【請客吃飯】慶祝升官，發給全員 10萬！", "pay_all", 100000),
    ("【車禍理賠】肇事修車，賠償 40萬！", "money", -400000), ("【聯準會升息】資金派對結束，縮水 60萬！", "money", -600000),
    ("【通膨數據爆表】消費冷清，損失 40萬！", "money", -400000), ("【全球大斷鏈】工廠停工，暫停行動一回合！", "skip", 1),
    ("【競爭對手倒閉】市占提升，獲利 70萬！", "money", 700000), ("【外媒看好台灣】熱錢湧入，獲利 50萬！", "money", 500000),
    ("【比特幣大暴漲】加密幣翻倍，獲得 40萬！", "money", 400000), ("【國稅局大查帳】抓到漏稅，損失 50萬！", "money", -500000)
]

# ==========================================
# [2] 核心類別區塊 (Classes)
# ==========================================
class Player:
    def __init__(self, name, role, token, color_theme, badge_color, is_ai=False):
        self.name = name
        self.role = role # 角色被動技能識別 ('外豬', '投信', '韭菜')
        self.token = token
        self.color_theme = color_theme  
        self.badge_color = badge_color
        self.money = 5000000
        self.position = 0
        self.is_bankrupt = False
        self.debt = 0
        self.skip_turns = 0
        self.inventory = [] 
        self.asset_history = [] 
        self.fixed_deposit = 0    
        self.has_insurance = False 
        self.warrants = [] # 權證清單(儲存 Tile index)
        self.is_ai = is_ai 

    def get_property_value(self, board):
        return sum(t.price + (t.upgrade_cost * t.level) for t in board if getattr(t, 'owner', None) == self)

    def get_total_asset(self, board):
        return self.money + self.fixed_deposit + self.get_property_value(board) - self.debt
        
    def get_max_pledge(self, board):
        return int(self.get_property_value(board) * 0.6)

    def record_history(self, board):
        self.asset_history.append(self.get_total_asset(board))
        
    def has_etf(self, board):
        sectors = set(t.sector for t in board if getattr(t, 'owner', None) == self and t.type == 'stock')
        req_len = 2 if self.role == '投信' else 3 # 投信只需2種產業即可觸發
        return len(sectors) >= req_len

class Tile:
    def __init__(self, index, name, tile_type, price=0, sector="無"):
        self.index = index
        self.name = name
        self.type = tile_type
        self.price = price
        self.sector = sector 
        self.base_rent = int(price * 0.1) if price > 0 else 0
        self.upgrade_cost = int(price * 0.5) if price > 0 else 0
        self.owner = None
        self.level = 0 

    def get_rent(self, owner_parks_count=1, macro_trend="平穩", board=None):
        rent = 0
        if self.type == 'stock': rent = self.base_rent * (2 ** self.level)
        elif self.type == 'park': rent = 100000 * owner_parks_count 
        
        # 總經影響
        if macro_trend == "全面牛市": rent = int(rent * 1.5)
        elif macro_trend == "全面熊市": rent = int(rent * 0.5)
        elif macro_trend == "科技爆發" and self.sector == "科技": rent = int(rent * 2.0)
        elif macro_trend == "金融寒冬" and self.sector == "金融": rent = int(rent * 0.5)
        elif macro_trend == "傳產復甦" and self.sector == "傳產": rent = int(rent * 1.5)
        
        if self.owner and board and self.owner.has_etf(board): rent = int(rent * 1.2)
        if self.owner and self.index in self.owner.warrants: rent *= 3 # 權證 3 倍爆擊
            
        return rent

# ==========================================
# [3] 遊戲邏輯與引擎區塊 (Logic)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_real_stock_prices():
    stock_map = {"聯電":"2303.TW", "日月光投控":"3711.TW", "台達電":"2308.TW", "京元電子":"2449.TW", "瑞昱":"2379.TW", "緯創":"3231.TW", "廣達":"2382.TW", "英業達":"2356.TW", "鴻海":"2317.TW", "世芯-KY":"3661.TW", "大立光":"3008.TW", "台積電":"2330.TW", "華碩":"2357.TW", "富邦金":"2881.TW", "國泰金":"2882.TW", "中信金":"2891.TW", "中鋼":"2002.TW", "長榮":"2603.TW", "台泥":"1101.TW", "中華電":"2412.TW", "台灣大":"3045.TW", "遠傳":"4904.TW"}
    prices = {}
    if YF_AVAILABLE:
        try:
            data = yf.download(list(stock_map.values()), period="1d", progress=False)['Close']
            if not data.empty:
                for name, ticker in stock_map.items():
                    if ticker in data.columns and not data[ticker].isna().all():
                        prices[name] = int(float(data[ticker].iloc[-1]) * 10000)
        except: pass
    return prices

def generate_board():
    real_prices = fetch_real_stock_prices()
    tiles = []
    data = [
        ('start',"起點 (領薪/股息)",0,"無"),('stock',"聯電",800000,"科技"),('chance',"機會",0,"無"),('stock',"日月光投控",900000,"科技"),('quiz',"🎓財經小學堂",0,"無"),('park',"內科",1500000,"園區"),('stock',"台達電",1000000,"科技"),('stock',"京元電子",1100000,"科技"),('fate',"命運",0,"無"),('stock',"瑞昱",1200000,"科技"),
        ('park',"南科",3000000,"園區"),('stock',"緯創",1300000,"科技"),('stock',"富邦金",1400000,"金融"),('chance',"機會",0,"無"),('stock',"國泰金",1500000,"金融"),('quiz',"🎓財經小學堂",0,"無"),('park',"竹科",2000000,"園區"),('stock',"中信金",1600000,"金融"),('stock',"中鋼",1700000,"傳產"),('fate',"命運",0,"無"),
        ('jail',"🚨 坐牢(停2回)",0,"無"),('stock',"長榮",1800000,"傳產"),('stock',"台泥",1900000,"傳產"),('stock',"廣達",2000000,"科技"),('chance',"機會",0,"無"),('stock',"英業達",2200000,"科技"),('tax',"☠️營業稅",200000,"無"),('park',"中科",2500000,"園區"),('stock',"鴻海",2500000,"科技"),('stock',"中華電",2600000,"傳產"),
        ('chance',"機會",0,"無"),('stock',"台灣大",2800000,"傳產"),('stock',"遠傳",2900000,"傳產"),('stock',"華碩",3000000,"科技"),('chance',"機會",0,"無"),('stock',"世芯-KY",3500000,"科技"),('tax',"☠️碳費",300000,"無"),('stock',"大立光",3800000,"科技"),('fate',"命運",0,"無"),('stock',"台積電",5000000,"科技")
    ]
    for idx, (t_type, t_name, def_price, t_sector) in enumerate(data):
        tiles.append(Tile(idx, t_name, t_type, real_prices.get(t_name, def_price) if t_type == 'stock' else def_price, t_sector))
    return tiles

def log(msg): st.session_state.logs.insert(0, msg)

def check_bankruptcy(player):
    if player.money < 0 and not player.is_bankrupt:
        if player.money + player.get_max_pledge(st.session_state.board) + player.fixed_deposit < 0:
            player.is_bankrupt = True
            log(f"💀 【破產宣告】{player.name} 包含定存與變賣資產後仍無法償還負債，黯然退場！")
            st.session_state.sfx_to_play = "fail"
            for t in st.session_state.board:
                if t.owner == player: t.owner, t.level = None, 0
        else:
            log(f"⚠️ {player.name} 現金為負，已自動啟動資產質押與定存週轉！")

def process_event(player, event_data, all_players):
    msg, action, value = event_data
    if action == "money" and value <= -400000 and player.has_insurance:
        player.has_insurance = False; st.session_state.sfx_to_play = "tada"
        return f"🛡️ 【保險理賠】意外險生效！保險公司吸收了鉅額損失：{msg}"
    if ((action == "money" and value < 0) or action in ["skip", "jail", "pay_all"]) and "🛡️免死金牌" in player.inventory:
        player.inventory.remove("🛡️免死金牌"); st.session_state.sfx_to_play = "tada"
        return f"🛡️ 發動【免死金牌】！成功抵銷原有的厄運：{msg}"
        
    if action == "money": player.money += value
    elif action == "skip": player.skip_turns += value
    elif action == "jail": player.position, player.skip_turns = 20, player.skip_turns + 2
    elif action == "collect_all":
        for p in all_players:
            if p != player and not p.is_bankrupt: p.money -= value; player.money += value; check_bankruptcy(p)
    elif action == "pay_all":
        for p in all_players:
            if p != player and not p.is_bankrupt: player.money -= value; p.money += value
    elif action == "item": player.inventory.append(value); msg += f" (獲得道具：{value})"
    return msg

def draw_card(player, is_chance):
    ev = random.choice(CHANCE_CARDS if is_chance else FATE_CARDS)
    st.session_state.sfx_to_play = "fail" if ev[1] in ["jail", "pay_all", "skip"] or (ev[1] == "money" and ev[2] < 0) else "tada"
    return process_event(player, ev, st.session_state.players)

def handle_movement(p, dice):
    old_pos = p.position
    p.position = (p.position + dice) % 40
    
    # 起點股息發放 (角色被動技能)
    if p.position < old_pos and p.position != 20: 
        div_rate = 0.08 if p.role == '外豬' else 0.05
        dividend = int(p.get_property_value(st.session_state.board) * div_rate)
        p.money += (2000000 + dividend)
        log(f"🎉 {p.name} 經過起點！領取薪資 200萬，並獲發年度股息 {dividend:,} 元！")
        st.session_state.sfx_to_play = "tada"
    
    tile = st.session_state.board[p.position]
    log(f"{p.name} 移動 {dice} 點，來到【{tile.name}】")
    
    if tile.type in ['stock', 'park']:
        if tile.owner is None: st.session_state.phase = 'action'
        elif tile.owner == p:
            if tile.level < 4: st.session_state.phase = 'action' 
            else: st.session_state.phase = 'next'
        else:
            cnt = sum(1 for t in st.session_state.board if getattr(t, 'type', '') == 'park' and getattr(t, 'owner', None) == tile.owner) if tile.type == 'park' else 1
            rent = tile.get_rent(cnt, st.session_state.macro_trend, st.session_state.board)
            
            # 韭菜被動技能：熊市額外懲罰
            if p.role == '韭菜' and st.session_state.macro_trend == '全面熊市': rent = int(rent * 1.2)
                
            if "🛡️免死金牌" in p.inventory:
                p.inventory.remove("🛡️免死金牌"); log(f"🛡️ 免死金牌擋下 {rent:,} 元過路費！"); st.session_state.sfx_to_play = "tada"
            else:
                p.money -= rent; tile.owner.money += rent; log(f"💸 踩到地雷！支付給 {tile.owner.name} 過路費 {rent:,} 元"); st.session_state.sfx_to_play = "fail"
            st.session_state.phase = 'next'
    elif tile.type == 'chance': st.session_state.phase = 'wait_chance'
    elif tile.type == 'fate': st.session_state.phase = 'wait_fate'
    elif tile.type == 'quiz': st.session_state.current_quiz = random.choice(QUIZ_BANK); st.session_state.phase = 'quiz'
    elif tile.type == 'jail':
        if "🛡️免死金牌" in p.inventory: p.inventory.remove("🛡️免死金牌"); log("🛡️ 免死金牌免除坐牢！"); st.session_state.sfx_to_play = "tada"
        else: p.skip_turns += 2; log("🚨 直接被捕！立刻停留在坐牢格 2 回合。"); st.session_state.sfx_to_play = "fail"
        st.session_state.phase = 'next'
    elif tile.type == 'tax':
        if "🛡️免死金牌" in p.inventory: p.inventory.remove("🛡️免死金牌"); log(f"🛡️ 免死金牌合法避稅 {tile.price:,} 元！")
        elif p.role == '韭菜' and random.random() < 0.3:
            p.money += 100000; log(f"🎉 散戶政策紅利！政府退稅紅包 100,000 元！"); st.session_state.sfx_to_play = "tada"
        else: p.money -= tile.price; log(f"☠️ 繳交稅金 {tile.price:,} 元。"); st.session_state.sfx_to_play = "fail"
        st.session_state.phase = 'next'
    else: st.session_state.phase = 'next'
    check_bankruptcy(p)

def next_turn():
    for p in st.session_state.players: 
        p.record_history(st.session_state.board)
        check_bankruptcy(p) 
        if p.fixed_deposit > 0 and not p.is_bankrupt:
            interest = int(p.fixed_deposit * 0.05); p.fixed_deposit += interest; log(f"🏦 {p.name} 定存產生複利 {interest:,} 元！")
            
    active_players = [p for p in st.session_state.players if not p.is_bankrupt]
    if len(active_players) <= 1:
        st.session_state.game_over = True
        if active_players: log(f"🏆 恭喜 {active_players[0].name} 成為最後贏家！")
        return

    # 總經輪動與權證斷頭
    if random.random() < 0.20:
        st.session_state.macro_trend = random.choice(["全面牛市", "全面熊市", "平穩", "科技爆發", "金融寒冬", "傳產復甦"])
        log(f"🌍 總經重大新聞！市場進入【{st.session_state.macro_trend}】")
        if st.session_state.macro_trend == "全面熊市":
            for p_check in active_players:
                if p_check.warrants:
                    penalty = len(p_check.warrants) * 100000
                    p_check.money -= penalty
                    p_check.warrants = []
                    log(f"💥 熊市襲來！{p_check.name} 的權證全部斷頭，並遭追繳 {penalty:,} 元！")
        
    st.session_state.phase = 'roll'
    st.session_state.hsr_active = False 
    
    while True:
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % len(st.session_state.players)
        p = st.session_state.players[st.session_state.turn_idx]
        if not p.is_bankrupt:
            if p.skip_turns > 0:
                p.skip_turns -= 1; log(f"⏸️ 【禁足】{p.token} {p.name} 還需暫停 {p.skip_turns} 回合！"); st.session_state.sfx_to_play = "fail"
                continue
            break

# ==========================================
# [4] JSON 存檔系統
# ==========================================
def get_save_data():
    save_dict = {
        'players': [{
            'name': p.name, 'role': p.role, 'token': p.token, 'color_theme': p.color_theme, 'badge_color': p.badge_color,
            'money': p.money, 'position': p.position, 'is_bankrupt': p.is_bankrupt,
            'debt': p.debt, 'skip_turns': p.skip_turns, 'is_ai': p.is_ai,
            'inventory': p.inventory, 'fixed_deposit': p.fixed_deposit, 'has_insurance': p.has_insurance, 'warrants': p.warrants
        } for p in st.session_state.players],
        'board': [{'owner_idx': st.session_state.players.index(t.owner) if t.owner else None, 'level': t.level} for t in st.session_state.board],
        'turn_idx': st.session_state.turn_idx, 'logs': st.session_state.logs, 'phase': st.session_state.phase, 
        'game_over': st.session_state.game_over, 'macro_trend': st.session_state.get('macro_trend', '平穩')
    }
    return json.dumps(save_dict, ensure_ascii=False).encode('utf-8')

def load_save_data(uploaded_file):
    try:
        save_dict = json.loads(uploaded_file.read().decode('utf-8'))
        players = []
        for pd in save_dict['players']:
            p = Player(pd['name'], pd.get('role', pd['name']), pd['token'], pd['color_theme'], pd['badge_color'], pd['is_ai'])
            p.money, p.position, p.is_bankrupt, p.debt, p.skip_turns = pd['money'], pd['position'], pd['is_bankrupt'], pd['debt'], pd['skip_turns']
            p.inventory, p.fixed_deposit, p.has_insurance, p.warrants = pd.get('inventory', []), pd.get('fixed_deposit', 0), pd.get('has_insurance', False), pd.get('warrants', [])
            players.append(p)
        board = generate_board()
        for i, td in enumerate(save_dict['board']):
            board[i].level = td['level']
            if td['owner_idx'] is not None: board[i].owner = players[td['owner_idx']]
        st.session_state.players, st.session_state.board = players, board
        st.session_state.turn_idx, st.session_state.logs = save_dict['turn_idx'], save_dict['logs']
        st.session_state.phase, st.session_state.game_over = save_dict['phase'], save_dict.get('game_over', False)
        st.session_state.macro_trend = save_dict.get('macro_trend', '平穩')
        st.success("✅ 遊戲進度讀取成功！"); time.sleep(1); st.rerun()
    except Exception: st.error("❌ 讀取失敗：存檔損壞。")

def init_game(p1_ai, p2_ai, p3_ai):
    st.session_state.players = [
        Player("外豬", "外豬", "🦅", "#ffebee", "#d32f2f", is_ai=p1_ai), 
        Player("投信", "投信", "🏦", "#e3f2fd", "#1976D2", is_ai=p2_ai), 
        Player("韭菜", "韭菜", "🌱", "#e8f5e9", "#388E3C", is_ai=p3_ai)  
    ]
    st.session_state.board, st.session_state.turn_idx = generate_board(), 0
    st.session_state.logs = ["🎮 遊戲開始！初始營運資金 5,000,000 元。"]
    st.session_state.phase, st.session_state.macro_trend = 'roll', "平穩" 
    st.session_state.game_over, st.session_state.sfx_to_play, st.session_state.hsr_active = False, "", False 

# ==========================================
# [5] UI 渲染區塊 (UI)
# ==========================================
def get_tile_colors(tile):
    if tile.type == 'start': return "#E8F5E9", "#4CAF50", "#333"
    if tile.type == 'jail': return "#424242", "#000000", "#FFF" 
    if tile.type == 'chance': return "#FF9800", "#E65100", "#FFF"
    if tile.type == 'fate': return "#9C27B0", "#4A148C", "#FFF"
    if tile.type == 'quiz': return "#E1F5FE", "#1565C0", "#333" 
    if tile.type == 'park': return "#E3F2FD", "#2196F3", "#333"
    if tile.sector == '科技': return "#EDE7F6", "#673AB7", "#333"
    if tile.sector == '金融': return "#FFF9C4", "#FFC107", "#333"
    if tile.sector == '傳產': return "#EFEBE9", "#795548", "#333"
    return "#ECEFF1", "#607D8B", "#333"

def get_board_html(dice_state=None, dice_val=None):
    board, active_p = st.session_state.board, st.session_state.players[st.session_state.turn_idx]
    level_map_short = {1: "一", 2: "二", 3: "先", 4: "超"}
    
    if dice_state == 'rolling':
        center_content = f'<div style="margin-top:20px; text-align:center;"><h2 style="color:#555; font-size:24px; margin-bottom:0;">🎲 擲骰子中...</h2><h1 style="font-size:120px; filter: blur(3px); margin:0;">{dice_val}</h1></div>'
    elif dice_state == 'result':
        center_content = f'<div style="margin-top:20px; text-align:center; animation: super-bounce 0.5s;"><h2 style="color:#D32F2F; font-size:28px; margin-bottom:0;">🚀 移動步數</h2><h1 style="font-size:150px; color:#E91E63; font-weight:bold; margin:0; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);">{dice_val}</h1></div>'
    elif st.session_state.phase in ['show_chance', 'show_fate'] and hasattr(st.session_state, 'drawn_card_msg'):
        card_type, card_color = ("🌟 機會卡", "#FF9800") if 'chance' in st.session_state.phase else ("⛈️ 命運卡", "#9C27B0")
        center_content = f'<div style="margin-top:20px; background:{card_color}; padding:30px; border-radius:20px; color:white; text-align:center; box-shadow: 0 15px 40px rgba(0,0,0,0.8); border: 8px solid white; animation: super-bounce 0.6s; max-width: 80%;"><h2 style="margin:0; font-size:45px; text-shadow: 2px 2px 4px rgba(0,0,0,0.4);">{card_type}</h2><p style="font-size:28px; font-weight:bold; margin-top:20px; line-height:1.3;">{st.session_state.drawn_card_msg}</p></div>'
    elif st.session_state.phase in ['wait_chance', 'wait_fate']:
        card_type = "🌟 機會" if 'chance' in st.session_state.phase else "⛈️ 命運"
        center_content = f'<div style="margin-top:40px; animation: highlight-bounce 1s infinite; text-align:center;"><h1 style="color:#1e3c72; font-size:55px; text-shadow: 2px 2px 10px rgba(255,255,255,0.8);">👉 請抽取<br>{card_type}卡！</h1></div>'
    else:
        trend = st.session_state.macro_trend
        trend_icon = "🚀" if trend in ["全面牛市", "科技爆發", "傳產復甦"] else "📉" if trend in ["全面熊市", "金融寒冬"] else "⚖️"
        trend_color = "#D32F2F" if "牛" in trend or "爆發" in trend or "復甦" in trend else "#1976D2" if "熊" in trend or "寒冬" in trend else "#333"
        center_content = f'<div style="margin-top:20px; text-align:center;"><h1 class="center-title">💰 台股大富翁</h1><h3 style="color:{trend_color}; font-size:28px; font-weight:bold; margin-top:10px;">總經新聞：{trend_icon} {trend}</h3><div class="card-deck"><div class="game-card card-chance">機會<br>🌟</div><div class="game-card card-fate">命運<br>⛈️</div></div></div>'

    html = "<style>.board-container { display: flex; justify-content: center; padding: 10px; background: #2c3e50; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }.grid-board { display: grid; grid-template-columns: repeat(11, 1fr); grid-template-rows: repeat(11, 1fr); gap: 3px; width: 100%; min-width: 1000px; height: 950px; background-color: #111; border: 4px solid #000; }.tile { background-color: #fff; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; text-align: center; font-family: '微軟正黑體', sans-serif; position: relative; overflow: hidden; cursor: help; }.color-bar { width: 100%; height: 18px; display: flex; align-items: center; justify-content: center; color: white; font-size: 11px; font-weight: bold; }.tile-name { font-size: 15px; font-weight: 900; margin-top: 4px; line-height: 1.1; padding: 0 2px; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);}.tile-price { font-size: 14px; font-weight: bold; margin-top: 2px;}.owner-badge { color: white; font-size: 13px; font-weight: bold; padding: 2px 4px; border-radius: 4px; margin-top: 2px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3); display:inline-block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:90%;}.players-area { margin-top: auto; padding-bottom: 2px; display: flex; justify-content: center; align-items: flex-end; height: 45px;}.token-normal { font-size: 30px; margin: 0 -3px; filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.4)); opacity: 0.8;}.active-token { font-size: 55px; margin: 0 -5px; z-index: 999; position: relative; animation: super-bounce 0.6s infinite alternate; filter: drop-shadow(0px 0px 15px rgba(255, 255, 0, 1)) drop-shadow(0px 0px 25px rgba(255, 0, 0, 0.9)); }@keyframes super-bounce { 0% { transform: translateY(0) scale(1); } 100% { transform: translateY(-15px) scale(1.1); } }@keyframes highlight-bounce { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }.center-space { grid-column: 2 / 11; grid-row: 2 / 11; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); display: flex; flex-direction: column; justify-content: flex-start; align-items: center; border: 4px dashed #999; position: relative;}.center-title { font-size: 56px; color: #1e3c72; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin: 0; }.card-deck { display: flex; gap: 40px; margin-top: 30px; justify-content: center;}.game-card { width: 110px; height: 150px; border-radius: 12px; display: flex; justify-content: center; align-items: center; font-size: 30px; font-weight: bold; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.3); border: 4px solid white; text-shadow: 1px 1px 5px rgba(0,0,0,0.5); transform: rotate(-5deg); transition: transform 0.3s;}.game-card:hover { transform: scale(1.1) rotate(0deg); }.card-chance { background: linear-gradient(45deg, #FF9800, #FFC107); }.card-fate { background: linear-gradient(45deg, #9C27B0, #E91E63); transform: rotate(5deg); }</style>"
    html += f'<div class="board-container"><div class="grid-board"><div class="center-space">{center_content}</div>'

    for tile in board:
        if 0 <= tile.index <= 10: r, c = 11, 11 - tile.index
        elif 11 <= tile.index <= 20: r, c = 11 - (tile.index - 10), 1
        elif 21 <= tile.index <= 30: r, c = 1, 1 + (tile.index - 20)
        else: r, c = 1 + (tile.index - 30), 11

        bg_color, bar_color, text_color = get_tile_colors(tile)
        players_html = "".join([f"<span class='{'active-token' if p == active_p else 'token-normal'}'>{getattr(p, 'token', '👤')}</span>" for p in st.session_state.players if p.position == tile.index and not p.is_bankrupt])
        
        hover_txt = f"{tile.name} ({tile.sector})"
        if tile.type in ['stock', 'park']:
            if tile.owner:
                cnt = sum(1 for temp_t in board if getattr(temp_t, 'type', '') == 'park' and getattr(temp_t, 'owner', None) == tile.owner) if tile.type == 'park' else 1
                hover_txt += f" | 所有人: {tile.owner.name} | 過路費: {tile.get_rent(cnt, st.session_state.macro_trend, board):,}元"
            else: hover_txt += f" | 購買價: {tile.price:,}元"

        owner_html = ""
        if tile.owner:
            lvl = level_map_short.get(tile.level, "")
            lvl_str = f"({lvl})" if lvl else ""
            w_icon = "🔥" if tile.index in tile.owner.warrants else ""
            owner_html = f"<div class='owner-badge' style='background-color:{tile.owner.badge_color};'>{w_icon}{tile.owner.name}{lvl_str}</div>"
            
        if tile.type == 'stock': price_html = f"<div class='tile-price' style='color:#d32f2f;'>${tile.price / 10000:.1f}</div>"
        elif tile.type == 'park': price_html = f"<div class='tile-price' style='color:#1976D2;'>${tile.price//10000}W</div>"
        else: price_html = ""
            
        html += f'<div class="tile" title="{hover_txt}" style="grid-row: {r}; grid-column: {c}; background-color: {bg_color};"><div class="color-bar" style="background-color: {bar_color};"></div><div class="tile-name" style="color: {text_color};">{tile.name.replace(" ", "<br>")}</div>{price_html}{owner_html}<div class="players-area">{players_html}</div></div>'
    html += "</div></div>"
    return html

# ==========================================
# [6] Streamlit 遊戲主程式
# ==========================================
st.set_page_config(page_title="台股大富翁 - 財商教育版", layout="wide")

if 'sfx_to_play' not in st.session_state: st.session_state.sfx_to_play = ""

if 'players' not in st.session_state:
    st.title("📈 台股大富翁 - 財商教育終極版")
    st.markdown("### 🎲 準備好學習投資理財了嗎？")
    
    col1, col2, col3 = st.columns(3)
    with col1: p1_type = st.selectbox("🦅 外豬 (被動技能：股息8%)", ["人類", "電腦 (AI)"])
    with col2: p2_type = st.selectbox("🏦 投信 (被動技能：雙產業ETF/答錯免罰)", ["人類", "電腦 (AI)"])
    with col3: p3_type = st.selectbox("🌱 韭菜 (被動技能：繳稅退稅/熊市雙殺)", ["人類", "電腦 (AI)"])
    
    if st.button("🚀 載入即時大盤並開始遊戲", type="primary", use_container_width=True):
        with st.spinner("📡 正在連線證交所取得即時股價..."):
            init_game(p1_type == "電腦 (AI)", p2_type == "電腦 (AI)", p3_type == "電腦 (AI)")
        st.rerun()
else:
    if st.session_state.game_over:
        st.balloons(); st.title("🏆 遊戲結束！賽後結算數據")
        fig = go.Figure()
        for p in st.session_state.players: fig.add_trace(go.Scatter(y=p.asset_history, mode='lines+markers', name=p.name))
        fig.update_layout(title="玩家總資產歷史走勢", xaxis_title="回合數", yaxis_title="總資產 (元)", height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.stop()

    with st.expander("💾 遊戲進度、結算與密技", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.download_button("⬇️ 下載目前存檔", data=get_save_data(), file_name=f"monopoly_{int(time.time())}.json", mime="application/json", use_container_width=True)
        with c2:
            uploaded_file = st.file_uploader("📂 讀取存檔", type=["json"], label_visibility="collapsed")
            if uploaded_file and st.button("讀取", use_container_width=True): load_save_data(uploaded_file)
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🏆 結算遊戲並查看圖表", use_container_width=True): st.session_state.game_over = True; st.rerun()
        with c4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💰 密技：+一千萬"): st.session_state.players[st.session_state.turn_idx].money += 10000000; st.rerun()

    st.markdown(f'<div style="display:flex; align-items:center; background:#f8f9fa; padding:5px 15px; border-radius:8px; margin-bottom:10px; border-left: 5px solid #4CAF50;"><span style="font-weight:bold; margin-right:15px; font-size:16px;">🎶 遊戲音樂:</span><audio id="bgm" src="{AUDIO_URLS["bgm"]}" controls autoplay loop style="height:35px;"></audio><span style="font-size:14px; color:#d32f2f; margin-left:15px; font-weight:bold;">👉 (請點擊上方播放鍵享受音樂！)</span></div>', unsafe_allow_html=True)

    col_board, col_ui = st.columns([3, 1])

    with col_board:
        board_placeholder = st.empty()
        board_placeholder.markdown(get_board_html(), unsafe_allow_html=True)
        
        st.markdown("### 📊 全體玩家資本儀表板")
        active_p = st.session_state.players[st.session_state.turn_idx]
        active_players = [p for p in st.session_state.players if not p.is_bankrupt]
        richest = max(active_players, key=lambda p: p.get_total_asset(st.session_state.board)) if active_players else None
        
        dash_cols = st.columns(len(st.session_state.players))
        for idx, p in enumerate(st.session_state.players):
            with dash_cols[idx]:
                if p.is_bankrupt: continue
                tot_ast = p.get_total_asset(st.session_state.board)
                skip = f"<span style='background:#D32F2F; color:white; padding:2px 6px; border-radius:8px; font-size:12px;'>⏸️ 停權 {p.skip_turns} 回</span>" if p.skip_turns > 0 else ""
                hl = "border: 4px solid #FF9800; box-shadow: 0 0 15px rgba(255, 152, 0, 0.5);" if p == active_p else "border: 2px solid #ccc; opacity: 0.7;"
                etf_badge = "🛡️ETF組合" if p.has_etf(st.session_state.board) else ""
                ins_badge = "🛟意外險" if p.has_insurance else ""
                
                card_html = f'<div style="background-color: {p.color_theme}; padding: 15px; border-radius: 12px; {hl}"><h4 style="margin: 0; color: #333;">{getattr(p, "token", "👤")} {p.name} {"👑" if p == richest else ""} {"(AI)" if p.is_ai else ""}</h4>{skip} <span style="font-size:12px; color:#1565C0; font-weight:bold;">{etf_badge} {ins_badge}</span><div style="margin-top:5px; font-weight:bold; color:#444;"><div style="margin-bottom:4px;">💰 現金: <span style="color:#2e7d32; font-size:15px;">{p.money:,}</span></div><div style="margin-bottom:4px;">🔒 定存: <span style="color:#E65100; font-size:15px;">{p.fixed_deposit:,}</span></div><div>🏦 總資產: <span style="color:#1565c0; font-size:15px;">{tot_ast:,}</span></div></div></div>'
                st.markdown(card_html, unsafe_allow_html=True)

    with col_ui:
        p = active_p
        st.info(f"👉 **當前回合：{getattr(p, 'token', '')} {p.name} {'(🤖 電腦)' if p.is_ai else ''}**\n\n📍 位置：第 {p.position} 格\n💰 現金：{p.money:,}")

        if st.session_state.phase == 'roll':
            if p.is_ai:
                st.warning("🤖 AI 正在決定步數...")
                time.sleep(1.0)
                if p.money > 1000000 and not p.has_insurance:
                    p.money -= 300000; p.has_insurance = True; log("🤖 AI 花費 30萬 購買了意外險。")
                handle_movement(p, random.randint(1, 6))
                st.rerun()
            else:
                # [新增功能 1] 銀行與保險
                with st.expander("🏦 銀行與保險業務", expanded=False):
                    st.write(f"**🔒 定存餘額: {p.fixed_deposit:,} 元** (每回合 5% 複利)")
                    dep_amount = st.number_input("存入/提領金額 (正=存，負=提)", step=100000, value=0)
                    if st.button("確認存提款", use_container_width=True):
                        if dep_amount > 0 and p.money >= dep_amount: p.money -= dep_amount; p.fixed_deposit += dep_amount; log(f"🏦 存入 {dep_amount:,} 元！"); st.rerun()
                        elif dep_amount < 0 and p.fixed_deposit >= abs(dep_amount): p.money += abs(dep_amount); p.fixed_deposit -= abs(dep_amount); log(f"🏦 提領 {abs(dep_amount):,} 元！"); st.rerun()
                        elif dep_amount != 0: st.error("餘額不足！")
                    st.divider()
                    if p.has_insurance: st.success("🛡️ 已擁有意外險 (抵銷大筆厄運扣款)")
                    elif st.button("🛟 購買意外險 (30萬)", use_container_width=True):
                        if p.money >= 300000: p.money -= 300000; p.has_insurance = True; log("🛡️ 成功購買意外險！"); st.rerun()
                        else: st.error("現金不足！")

                # [新增功能 2] 權證交易所
                with st.expander("📈 證券交易所 (發行權證)", expanded=False):
                    st.write("花費 10萬 為名下股票發行權證，過路費變為 3倍！(注意：遇全面熊市將斷頭並罰款)")
                    owned_stocks = [t for t in st.session_state.board if t.owner == p and t.type == 'stock' and t.index not in p.warrants]
                    if owned_stocks:
                        w_tile = st.selectbox("選擇要發行權證的股票", owned_stocks, format_func=lambda t: t.name)
                        if st.button("🔥 發行權證 (-10萬)"):
                            if p.money >= 100000: p.money -= 100000; p.warrants.append(w_tile.index); log(f"📈 {p.name} 為 {w_tile.name} 發行了權證！"); st.session_state.sfx_to_play = "cash"; st.rerun()
                            else: st.error("現金不足！")
                    else: st.write("目前沒有可發行權證的股票。")

                # [新增功能 3] 主動變賣資產
                with st.expander("📉 資產變賣 (換取 70% 現金)", expanded=False):
                    owned_tiles = [t for t in st.session_state.board if t.owner == p]
                    if owned_tiles:
                        sell_tile = st.selectbox("選擇要變賣的資產", owned_tiles, format_func=lambda t: f"{t.name} (可換回 {int((t.price + t.upgrade_cost*t.level)*0.7):,} 元)")
                        if st.button("💸 確認變賣"):
                            sell_val = int((sell_tile.price + sell_tile.upgrade_cost*sell_tile.level)*0.7)
                            p.money += sell_val; sell_tile.owner = None; sell_tile.level = 0
                            if sell_tile.index in p.warrants: p.warrants.remove(sell_tile.index)
                            log(f"📉 {p.name} 變賣了 {sell_tile.name}，獲得 {sell_val:,} 元。"); st.session_state.sfx_to_play = "cash"; st.rerun()
                    else: st.write("目前沒有可變賣的資產。")

                # 道具系統
                if p.inventory:
                    with st.expander("🎒 使用道具", expanded=False):
                        if "🎲遙控骰子" in p.inventory:
                            chosen_dice = st.slider("選擇步數", 1, 6, 1)
                            if st.button("🚀 使用遙控骰子", type="primary", use_container_width=True): p.inventory.remove("🎲遙控骰子"); handle_movement(p, chosen_dice); st.rerun()
                        if "🚀高鐵卡" in p.inventory and st.button("🚄 使用高鐵卡 (步數 x2)", type="primary", use_container_width=True):
                            p.inventory.remove("🚀高鐵卡"); st.session_state.hsr_active = True; log(f"🚄 {p.name} 準備飆速！"); st.rerun()
                        if "💳查稅卡" in p.inventory and st.button("💳 使用查稅卡 (向全員收30萬)", type="primary", use_container_width=True):
                            p.inventory.remove("💳查稅卡")
                            for other in st.session_state.players:
                                if other != p and not other.is_bankrupt: other.money -= 300000; p.money += 300000
                            log(f"💳 {p.name} 使用查稅卡大賺一筆！"); st.session_state.sfx_to_play = "cash"; st.rerun()
                
                # 擲骰子
                btn_txt = "🎲 擲骰子 (高鐵飆速中!)" if getattr(st.session_state, 'hsr_active', False) else "🎲 擲骰子"
                if st.button(btn_txt, type="primary", use_container_width=True):
                    dice = random.randint(1, 6)
                    if getattr(st.session_state, 'hsr_active', False): dice *= 2; st.session_state.hsr_active = False 
                        
                    st.markdown(f'<audio autoplay><source src="{AUDIO_URLS["dice"]}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
                    for i in range(5): 
                        board_placeholder.markdown(get_board_html('rolling', random.randint(1, 6)), unsafe_allow_html=True); time.sleep(0.1)
                    
                    board_placeholder.markdown(get_board_html('result', dice), unsafe_allow_html=True)
                    st.markdown(f'<audio autoplay><source src="{AUDIO_URLS["footstep"]}" type="audio/mpeg"></audio>', unsafe_allow_html=True); time.sleep(0.8) 
                    handle_movement(p, dice); st.rerun()
                
        elif st.session_state.phase == 'action':
            tile = st.session_state.board[p.position]
            lvl_map = {1: "一廠", 2: "二廠", 3: "先進製程", 4: "超級工廠"}
            if p.is_ai:
                time.sleep(1.2)
                if tile.owner is None and p.money > tile.price * 1.3:
                    p.money -= tile.price; tile.owner = p; log(f"🤖 AI 買下【{tile.name}】")
                elif tile.owner == p and tile.level < 4 and p.money > tile.upgrade_cost * 1.5:
                    p.money -= tile.upgrade_cost; tile.level += 1; log(f"🤖 AI 升級【{tile.name}】")
                st.session_state.phase = 'next'; st.rerun()
            else:
                if tile.owner is None:
                    st.warning(f"是否投資【{tile.name}】？\n\n價格：{tile.price:,} 元")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ 確定投資", type="primary", use_container_width=True):
                        if p.money >= tile.price: p.money -= tile.price; tile.owner = p; log(f"🤝 收購【{tile.name}】"); st.session_state.sfx_to_play = "cash"
                        else: log(f"❌ 現金不足"); st.session_state.sfx_to_play = "fail"
                        st.session_state.phase = 'next'; st.rerun()
                    if c2.button("❌ 放棄", use_container_width=True): st.session_state.phase = 'next'; st.rerun()
                elif tile.owner == p and tile.level < 4:
                    st.warning(f"是否升級至 {lvl_map[tile.level+1]}？\n\n費用：{tile.upgrade_cost:,} 元")
                    c1, c2 = st.columns(2)
                    if c1.button("🏗️ 確定升級", type="primary", use_container_width=True):
                        if p.money >= tile.upgrade_cost: p.money -= tile.upgrade_cost; tile.level += 1; log(f"🏗️ 升級 {lvl_map[tile.level]}！"); st.session_state.sfx_to_play = "cash"
                        else: log(f"❌ 現金不足"); st.session_state.sfx_to_play = "fail"
                        st.session_state.phase = 'next'; st.rerun()
                    if c2.button("❌ 暫不升級", use_container_width=True): st.session_state.phase = 'next'; st.rerun()

        # [新增功能 4] 財經小學堂
        elif st.session_state.phase == 'quiz':
            q_data = st.session_state.current_quiz
            if p.is_ai:
                time.sleep(1.5)
                # AI 假設有 80% 機率答對
                if random.random() < 0.8:
                    p.money += 200000; log(f"🤖 🎓 AI 答對問題！獲得 20萬。")
                else:
                    if p.role == '投信': log(f"🤖 🎓 AI 答錯，但法人免學費。")
                    else: p.money -= 100000; log(f"🤖 ❌ AI 答錯！繳交 10萬。")
                st.session_state.phase = 'next'; st.rerun()
            else:
                st.warning("🎓 **財經小學堂！** 答對拿 20萬，答錯扣 10萬！")
                st.markdown(f"### Q: {q_data['q']}")
                ans = st.radio("請選擇答案：", q_data['opts'], index=None)
                if st.button("📝 提交答案", type="primary", use_container_width=True):
                    if ans:
                        if q_data['opts'].index(ans) == q_data['ans']:
                            p.money += 200000; log(f"🎓 {p.name} 答對了！獲得獎學金 20萬！解析：{q_data['exp']}"); st.session_state.sfx_to_play = "tada"
                        else:
                            if p.role == '投信': log(f"❌ 答錯了！但投信法人免扣學費。解析：{q_data['exp']}")
                            else: p.money -= 100000; log(f"❌ {p.name} 答錯了！繳交學費 10萬。解析：{q_data['exp']}"); st.session_state.sfx_to_play = "fail"
                        st.session_state.phase = 'next'; st.rerun()
                    else: st.error("請先選擇答案！")

        elif st.session_state.phase in ['wait_chance', 'wait_fate']:
            if p.is_ai:
                time.sleep(1.0)
                st.session_state.drawn_card_msg = draw_card(p, st.session_state.phase == 'wait_chance')
                st.session_state.phase = 'show_chance' if st.session_state.phase == 'wait_chance' else 'show_fate'; st.rerun()
            else:
                c_name = "機會" if st.session_state.phase == 'wait_chance' else "命運"
                st.warning(f"🌟 請抽取卡牌。")
                if st.button(f"🌟 抽取{c_name}卡", type="primary", use_container_width=True):
                    st.session_state.drawn_card_msg = draw_card(p, st.session_state.phase == 'wait_chance')
                    st.session_state.phase = 'show_chance' if st.session_state.phase == 'wait_chance' else 'show_fate'; st.rerun()
                
        elif st.session_state.phase in ['show_chance', 'show_fate']:
            if p.is_ai: time.sleep(2.5); st.session_state.phase = 'next'; next_turn(); st.rerun()
            else:
                st.success("請查看地圖上方的卡片內容！")
                if st.button("🔚 確定並結束回合", type="primary", use_container_width=True): st.session_state.phase = 'next'; next_turn(); st.rerun()

        elif st.session_state.phase == 'next':
            if p.is_ai: time.sleep(0.5); next_turn(); st.rerun()
            else:
                if st.button("🔚 結束回合", type="primary", use_container_width=True): next_turn(); st.rerun()
                
        logs_html = "<div style='background:#f1f3f5; padding:10px; border-radius:10px; height:500px; overflow-y:auto; color:#333;'>"
        for i, m in enumerate(st.session_state.logs[:30]): logs_html += f"<p style='margin:4px 0; border-bottom:1px solid #ddd; padding-bottom:4px; font-size:14px;'>{'🔥 ' if i==0 else ''}{m}</p>"
        logs_html += "</div>"
        st.markdown(logs_html, unsafe_allow_html=True)

if st.session_state.get('sfx_to_play'):
    st.markdown(f'<audio autoplay><source src="{AUDIO_URLS[st.session_state.sfx_to_play]}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
    st.session_state.sfx_to_play = ""