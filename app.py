"""FurniGo BI dashboard on PostgreSQL.

Part A: daily business operations (sample marketplace data, Feb-Mar 2027 moving season)
Part B: survey insights (real data, 20 responses)

Run:  streamlit run app.py
Connection: sidebar fields (defaults from PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD),
or one DATABASE_URL in the environment or .streamlit/secrets.toml.
"""
import os
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

st.set_page_config(page_title="FurniGo BI Dashboard", page_icon="🛋️", layout="wide")

BLUE = ["#2563eb", "#38bdf8", "#1d4ed8", "#7dd3fc", "#93c5fd", "#1e40af", "#60a5fa", "#bfdbfe"]
BLUE_SCALE = ["#bfdbfe", "#1d4ed8"]
YEN = st.column_config.NumberColumn(format="¥%d")


# ---------- Connection ----------
def secret_url():
    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return os.environ.get("DATABASE_URL")


def build_url():
    url = secret_url()
    if url:
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                url = "postgresql+psycopg://" + url[len(prefix):]
        return url
    with st.sidebar:
        st.header("Database")
        host = st.text_input("Host", os.environ.get("PGHOST", "localhost"))
        port = st.text_input("Port", os.environ.get("PGPORT", "5432"))
        name = st.text_input("Database", os.environ.get("PGDATABASE", "furnigo"))
        user = st.text_input("User", os.environ.get("PGUSER", "postgres"))
        pw = st.text_input("Password", os.environ.get("PGPASSWORD", ""), type="password")
    return URL.create("postgresql+psycopg", username=user, password=pw, host=host,
                      port=int(port), database=name).render_as_string(hide_password=False)


@st.cache_resource
def engine_for(url: str):
    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=60, show_spinner=False)
def run(url: str, sql: str, params: tuple = ()) -> pd.DataFrame:
    with engine_for(url).connect() as conn:
        return pd.read_sql(text(sql), conn, params=dict(params))


URL_STR = build_url()
try:
    run(URL_STR, "SELECT 1")
    run(URL_STR, "SELECT 1 FROM survey_responses LIMIT 1")
except Exception as exc:
    st.title("🛋️ FurniGo")
    st.error("Could not connect to the FurniGo database, or the tables are missing. Check the "
             "connection details in the sidebar and confirm 00_run_all.sql was run (see README).")
    st.code(str(exc).splitlines()[0])
    st.stop()


def q(sql, **params):
    return run(URL_STR, sql, tuple(params.items()))


def show_sql(sql):
    with st.expander("Show the SQL", expanded=True):
        st.code(sql.strip(), language="sql")


def blank(fig):
    fig.update_layout(margin=dict(t=20, b=10))
    return fig


# ---------- Navigation ----------
PAGES = {
    "Overview": None,
    "A1 · Match a buyer request": "a1",
    "A2 · Leaving-soon deals": "a2",
    "A3 · Seller ratings": "a3",
    "A4 · Monthly sales and revenue": "a4",
    "A5 · Unmet demand": "a5",
    "B1 · Items students would buy used": "b1",
    "B2 · Price students will pay": "b2",
    "B3 · Frustrations with current options": "b3",
    "B4 · Interest by university": "b4",
    "B5 · Delivery fee willingness": "b5",
    "B6 · What builds trust": "b6",
}
with st.sidebar:
    st.header("Use case")
    page = st.radio("Pick one", list(PAGES), label_visibility="collapsed")
    st.caption("Part A uses sample marketplace data. Part B uses real survey data (20 responses).")

st.title("🛋️ FurniGo: Business Dashboard")
st.caption("Student furniture marketplace for Tokyo. All amounts in JPY.")
key = PAGES[page]


# ---------- Overview ----------
if key is None:
    st.subheader("Overview")
    k = q("""SELECT
      (SELECT COUNT(*) FROM listings WHERE status='available') AS live,
      (SELECT COUNT(*) FROM buyer_requests WHERE status='open') AS open_req,
      (SELECT COALESCE(SUM(sale_price),0) FROM transactions WHERE status='completed') AS gmv,
      (SELECT COUNT(*) FROM survey_responses) AS resp""").iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live listings", int(k.live))
    c2.metric("Open buyer requests", int(k.open_req))
    c3.metric("Sample GMV (Feb to Mar 2027)", f"¥{int(k.gmv):,}")
    c4.metric("Survey responses", int(k.resp))
    st.markdown(
        "**How FurniGo works.** Sellers list items with a move-out deadline. Buyers post what they "
        "need, where, by when, and their budget. The database matches the two when the item type and "
        "area agree, the price fits the budget, and the date windows overlap.\n\n"
        "Pick a use case in the sidebar. **A1 to A5** run on made-up marketplace data for the "
        "February to March 2027 moving season. **B1 to B6** run on the real survey."
    )
    st.info("The sample marketplace data is illustrative. Only the survey is real. Treat the survey "
            "as a small early signal: 13 of 20 responses come from one university (TIU).")
    st.subheader("Survey responses by university")
    show_sql("""SELECT un.name AS university, COUNT(*) AS responses
FROM survey_responses s JOIN universities un ON un.university_id = s.university_id
GROUP BY un.name ORDER BY responses DESC;""")
    df = q("""SELECT un.name AS university, COUNT(*) AS responses
FROM survey_responses s JOIN universities un ON un.university_id = s.university_id
GROUP BY un.name ORDER BY responses DESC""")
    st.plotly_chart(blank(px.bar(df.iloc[::-1], x="responses", y="university", orientation="h",
                                 color_discrete_sequence=BLUE, text="responses")), width="stretch")

# ---------- A1 ----------
elif key == "a1":
    st.subheader("A1 · Which listings match a buyer's request?")
    st.markdown("Rule: same item type, same area, price within budget, and the seller's available dates "
                "overlap the buyer's needed dates. Pick an open request to see its matches.")
    reqs = q("""SELECT r.request_id, u.display_name AS buyer, c.category_name,
       a.city || ', ' || a.neighborhood AS area, r.max_budget, r.needed_from, r.needed_until
FROM buyer_requests r JOIN users u ON u.user_id = r.buyer_id
JOIN categories c ON c.category_id = r.category_id JOIN areas a ON a.area_id = r.target_area_id
WHERE r.status = 'open' ORDER BY r.request_id""")
    labels = {f"#{r.request_id} · {r.buyer} wants {r.category_name} in {r.area}, up to ¥{r.max_budget:,}":
              int(r.request_id) for r in reqs.itertuples()}
    rid = labels[st.selectbox("Open buyer request", list(labels))]
    sql = """SELECT l.listing_id, l.title, l.price, r.max_budget,
       GREATEST(l.available_from, r.needed_from) AS pickup_from,
       LEAST(l.available_until, r.needed_until)  AS pickup_until
FROM listings l
JOIN buyer_requests r ON r.category_id = l.category_id AND r.target_area_id = l.pickup_area_id
WHERE r.request_id = :request_id
  AND l.status = 'available' AND r.status = 'open'
  AND l.price <= r.max_budget
  AND l.available_from <= r.needed_until
  AND l.available_until >= r.needed_from;"""
    show_sql(sql.replace(":request_id", str(rid)))
    df = q(sql.rstrip(";"), request_id=rid)
    if df.empty:
        st.warning("No listing matches this request. It counts as unmet demand (see A5).")
    else:
        st.success(f"{len(df)} matching listing(s)")
        st.dataframe(df, width="stretch", hide_index=True,
                     column_config={"price": YEN, "max_budget": YEN})
    st.subheader("All saved matches")
    show_sql("SELECT * FROM matches ORDER BY request_id;  -- filled from the v_listing_matches view")
    st.dataframe(q("""SELECT m.request_id, m.listing_id, l.title, m.match_score
FROM matches m JOIN listings l ON l.listing_id = m.listing_id ORDER BY m.request_id"""),
                 width="stretch", hide_index=True)

# ---------- A2 ----------
elif key == "a2":
    st.subheader("A2 · Which sellers are leaving soon?")
    st.markdown("Available listings whose seller moves out within a window of days. These are the "
                "deals to promote first.")
    a, b = st.columns(2)
    start = a.date_input("Today is", date(2027, 3, 20))
    days = b.slider("Window (days)", 1, 30, 7)
    sql = """SELECT l.title, u.display_name AS seller, un.name AS university,
       l.original_price, l.price,
       ROUND(100.0 * (l.original_price - l.price) / NULLIF(l.original_price, 0)) AS discount_pct,
       l.available_until - DATE :start AS days_left
FROM listings l
JOIN users u ON u.user_id = l.seller_id
JOIN universities un ON un.university_id = u.university_id
WHERE l.status = 'available'
  AND l.available_until BETWEEN DATE :start AND DATE :start + :days
ORDER BY days_left, discount_pct DESC;"""
    show_sql(sql.replace(":start", f"'{start}'").replace(":days", str(days)))
    df = q(sql.rstrip(";").replace("DATE :start", "CAST(:start AS date)"), start=str(start), days=days)
    if df.empty:
        st.info("No listings leave in that window.")
    else:
        fig = px.bar(df, x="title", y="days_left", color="discount_pct", text="days_left",
                     color_continuous_scale=BLUE_SCALE,
                     labels={"title": "", "days_left": "Days left", "discount_pct": "Discount %"})
        st.plotly_chart(blank(fig), width="stretch")
        st.dataframe(df, width="stretch", hide_index=True,
                     column_config={"original_price": YEN, "price": YEN})

# ---------- A3 ----------
elif key == "a3":
    st.subheader("A3 · Which sellers do buyers trust?")
    st.markdown("Average review scores per seller, from completed sales only.")
    sql = """SELECT u.display_name AS seller, un.name AS university,
       COUNT(rv.review_id) AS reviews,
       ROUND(AVG(rv.rating), 1) AS avg_rating,
       ROUND(AVG(rv.as_described_rating), 1) AS avg_as_described,
       ROUND(AVG(rv.on_time_rating), 1) AS avg_on_time
FROM reviews rv
JOIN transactions t ON t.transaction_id = rv.transaction_id
JOIN listings l ON l.listing_id = t.listing_id
JOIN users u ON u.user_id = l.seller_id
JOIN universities un ON un.university_id = u.university_id
WHERE t.status = 'completed'
GROUP BY u.display_name, un.name
ORDER BY avg_rating DESC, reviews DESC;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    for c in ["avg_rating", "avg_as_described", "avg_on_time"]:
        df[c] = df[c].astype(float)
    long = df.melt(id_vars=["seller", "reviews"], value_vars=["avg_rating", "avg_as_described", "avg_on_time"],
                   var_name="score", value_name="value")
    long["score"] = long["score"].map({"avg_rating": "Overall", "avg_as_described": "As described",
                                       "avg_on_time": "On time"})
    fig = px.bar(long, x="seller", y="value", color="score", barmode="group",
                 color_discrete_sequence=BLUE, labels={"value": "Average (1 to 5)", "seller": ""})
    fig.update_yaxes(range=[0, 5])
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption("Each seller has only 1 to 2 reviews, so these scores are illustrative.")

# ---------- A4 ----------
elif key == "a4":
    st.subheader("A4 · How much does FurniGo earn?")
    st.markdown("Monthly completed sales, plus FurniGo's revenue: an 8% commission on the sale price "
                "and the delivery fees collected.")
    sql = """SELECT DATE_TRUNC('month', t.completed_at)::date AS sale_month,
       COUNT(*) AS completed_orders,
       SUM(t.sale_price) AS gross_sales_yen,
       ROUND(SUM(t.sale_price) * 0.08) AS commission_yen,
       SUM(COALESCE(p.delivery_fee, 0)) AS delivery_fees_yen
FROM transactions t
LEFT JOIN pickup_bookings p ON p.transaction_id = t.transaction_id
WHERE t.status = 'completed'
GROUP BY 1 ORDER BY 1;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    for c in ["commission_yen", "gross_sales_yen", "delivery_fees_yen"]:
        df[c] = df[c].astype(float)
    df["revenue_yen"] = df["commission_yen"] + df["delivery_fees_yen"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Gross sales", f"¥{int(df.gross_sales_yen.sum()):,}")
    c2.metric("FurniGo revenue", f"¥{int(df.revenue_yen.sum()):,}")
    c3.metric("Revenue as % of sales", f"{100 * df.revenue_yen.sum() / df.gross_sales_yen.sum():.1f}%")
    long = df.melt(id_vars="sale_month", value_vars=["commission_yen", "delivery_fees_yen"],
                   var_name="source", value_name="yen")
    long["source"] = long["source"].map({"commission_yen": "Commission", "delivery_fees_yen": "Delivery fees"})
    long["sale_month"] = long["sale_month"].astype(str).str[:7]
    fig = px.bar(long, x="sale_month", y="yen", color="source", barmode="stack",
                 color_discrete_sequence=BLUE, labels={"sale_month": "Month", "yen": "Revenue (¥)"})
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True,
                 column_config={k: YEN for k in ["gross_sales_yen", "commission_yen",
                                                  "delivery_fees_yen", "revenue_yen"]})
    st.caption("Sample data, two months only. The 8% commission is an assumption, not a measured rate.")

# ---------- A5 ----------
elif key == "a5":
    st.subheader("A5 · Where is demand not being met?")
    st.markdown("Open buyer requests that no available listing matches. These tell us which items and "
                "areas to recruit sellers for.")
    sql = """SELECT c.category_name, a.city || ', ' || a.neighborhood AS area,
       COUNT(*) AS unmatched_requests
FROM buyer_requests r
JOIN categories c ON c.category_id = r.category_id
JOIN areas a ON a.area_id = r.target_area_id
WHERE r.status = 'open'
  AND NOT EXISTS (SELECT 1 FROM v_listing_matches m WHERE m.request_id = r.request_id)
GROUP BY c.category_name, area
ORDER BY unmatched_requests DESC, c.category_name;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    df["label"] = df["category_name"] + " · " + df["area"]
    fig = px.bar(df.iloc[::-1], x="unmatched_requests", y="label", orientation="h",
                 color_discrete_sequence=BLUE, text="unmatched_requests",
                 labels={"unmatched_requests": "Unmatched open requests", "label": ""})
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df.drop(columns="label"), width="stretch", hide_index=True)
    st.caption("All three gaps are in Tokyo (Ikebukuro, Takadanobaba). Most sample listings are in "
               "Saitama-area locations, which suggests where to recruit.")

# ---------- B1 ----------
elif key == "b1":
    st.subheader("B1 · Which items would students buy secondhand?")
    sql = """SELECT answer AS item, COUNT(*) AS students
FROM survey_answers
WHERE question_code = 'secondhand_items'
GROUP BY answer
ORDER BY students DESC, item;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    fig = px.bar(df.iloc[::-1], x="students", y="item", orientation="h", text="students",
                 color_discrete_sequence=BLUE, labels={"students": "Students (of 20)", "item": ""})
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption("Big appliances lead: washing machines (18 of 20) and fridges (17 of 20).")

# ---------- B2 ----------
elif key == "b2":
    st.subheader("B2 · The most students would pay, by item type")
    sql = """SELECT c.category_name, pb.price_band, COUNT(*) AS students
FROM survey_price_limits spl
JOIN categories c ON c.category_id = spl.category_id
JOIN price_bands pb ON pb.price_band = spl.price_band
GROUP BY c.category_name, pb.price_band, pb.sort_order
ORDER BY c.category_name, pb.sort_order;"""
    show_sql(sql)
    df = q("""SELECT c.category_name, pb.price_band, pb.sort_order, COUNT(*) AS students
FROM survey_price_limits spl
JOIN categories c ON c.category_id = spl.category_id
JOIN price_bands pb ON pb.price_band = spl.price_band
GROUP BY c.category_name, pb.price_band, pb.sort_order
ORDER BY c.category_name, pb.sort_order""")
    order = df.drop_duplicates("price_band").sort_values("sort_order")["price_band"].tolist()
    pivot = df.pivot(index="category_name", columns="price_band", values="students").reindex(columns=order).fillna(0)
    fig = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale=BLUE_SCALE,
                    labels={"x": "Price band", "y": "", "color": "Students"})
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df.drop(columns="sort_order"), width="stretch", hide_index=True)
    st.caption("Chairs and small items cluster under ¥3,000. Fridges and washers sit at ¥3,000 to ¥15,000. "
               "One respondent answered 'Over ¥15,000' for everything, which looks like an outlier.")

# ---------- B3 ----------
elif key == "b3":
    st.subheader("B3 · Biggest frustrations with current options")
    st.markdown("Mercari, Facebook groups and similar. Students could tick several.")
    sql = """SELECT answer AS frustration, COUNT(*) AS students
FROM survey_answers
WHERE question_code = 'frustrations'
GROUP BY answer
ORDER BY students DESC, frustration;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    fig = px.bar(df.iloc[::-1], x="students", y="frustration", orientation="h", text="students",
                 color_discrete_sequence=BLUE, labels={"students": "Students (of 20)", "frustration": ""})
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption("Pickup coordination is the top pain point, which supports date and pickup matching.")

# ---------- B4 ----------
elif key == "b4":
    st.subheader("B4 · Interest in FurniGo by university")
    sql = """SELECT un.name AS university,
       COUNT(*) AS responses,
       ROUND(AVG(s.interest_score), 1) AS avg_interest,
       ROUND(AVG(s.date_match_score), 1) AS avg_date_matching
FROM survey_responses s
JOIN universities un ON un.university_id = s.university_id
GROUP BY un.name
ORDER BY responses DESC, university;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    df["avg_interest"] = df["avg_interest"].astype(float)
    df["avg_date_matching"] = df["avg_date_matching"].astype(float)
    fig = px.bar(df.iloc[::-1], x="avg_interest", y="university", orientation="h", text="responses",
                 color_discrete_sequence=BLUE,
                 labels={"avg_interest": "Average interest (1 to 5)", "university": ""})
    fig.update_traces(texttemplate="n=%{text}")
    fig.update_xaxes(range=[0, 5])
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
    st.warning("Only TIU has more than one response (13 of 20). Single-response averages are not "
               "comparable. Collect more from other universities before drawing conclusions.")

# ---------- B5 ----------
elif key == "b5":
    st.subheader("B5 · How much would students pay for delivery?")
    sql = """SELECT delivery_fee_willing, COUNT(*) AS students
FROM survey_responses
GROUP BY delivery_fee_willing
ORDER BY students DESC;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    rank = ["I would only collect items myself", "≤ ¥500", "¥500–¥1000", "¥1,000–¥2000", "¥2,000–¥4000", "≥ ¥4,000"]
    df["o"] = df["delivery_fee_willing"].map({k: i for i, k in enumerate(rank)})
    chart = df.sort_values("o")
    fig = px.bar(chart, x="delivery_fee_willing", y="students", text="students",
                 color_discrete_sequence=BLUE,
                 labels={"delivery_fee_willing": "Fee students would accept", "students": "Students (of 20)"})
    fig.update_xaxes(categoryorder="array", categoryarray=rank)
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df.drop(columns="o"), width="stretch", hide_index=True)
    st.caption("The most common answer is ¥500 to ¥1,000 (7 of 20), but answers range widely. The sample data "
               "charges ¥500 per delivery, the low end of what students said.")

# ---------- B6 ----------
elif key == "b6":
    st.subheader("B6 · What makes students feel safe buying from another student?")
    sql = """SELECT answer AS safety_feature, COUNT(*) AS students
FROM survey_answers
WHERE question_code = 'safety_features'
GROUP BY answer
ORDER BY students DESC, safety_feature;"""
    show_sql(sql)
    df = q(sql.rstrip(";"))
    fig = px.bar(df.iloc[::-1], x="students", y="safety_feature", orientation="h", text="students",
                 color_discrete_sequence=BLUE, labels={"students": "Students (of 20)", "safety_feature": ""})
    st.plotly_chart(blank(fig), width="stretch")
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption("Real photos, refund protection and ratings lead. Verified university email ties for last, "
               "so student-ID checks alone may not be enough to build trust.")
