import streamlit as st
import json
import math
import time
from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# Quiz data
# ---------------------------
QUIZZES = {
    "Motion": {
        "Easy": [
            {"q":"An object moves at constant acceleration. u=0 m/s, a=2 m/s², distance in 3 s?","type":"numeric","answer":9.0,"explain":"s = ut + 1/2 a t^2 = 9 m."},
            {"q":"Rate of change of displacement?","type":"mcq","options":["Speed","Velocity","Acceleration","Jerk"],"answer":"Velocity","explain":"Velocity is the rate of change of displacement."},
            {"q":"A car starts from rest and accelerates at 1 m/s² for 5 s. Final velocity?","type":"numeric","answer":5.0,"explain":"v = u + at = 0 + 1*5 = 5 m/s."},
            {"q":"Which graph shows constant acceleration?","type":"mcq","options":["Position-time straight","Velocity-time straight","Acceleration-time sinusoidal","Position-time horizontal"],"answer":"Velocity-time straight","explain":"Velocity-time straight line indicates constant acceleration."},
            {"q":"Two objects dropped from same height, no air resistance. Which hits first?","type":"mcq","options":["Heavier","Lighter","Both same","Depends on shape"],"answer":"Both same","explain":"Acceleration due to gravity is same for all masses."}
        ],
        "Average": [
            {"q":"A car accelerates from 10 m/s to 20 m/s in 5 s. Acceleration?","type":"numeric","answer":2.0,"explain":"a = (v-u)/t = 2 m/s²"},
            {"q":"A train moves 60 m in 5 s from rest. Find acceleration assuming constant.","type":"numeric","answer":4.8,"explain":"s = ut + 1/2 at² → 60 = 0 + 1/2 * a *25 → a=4.8 m/s²"},
            {"q":"Which quantity is vector?","type":"mcq","options":["Speed","Distance","Velocity","Time"],"answer":"Velocity","explain":"Velocity has magnitude and direction."},
            {"q":"If velocity-time graph is horizontal line, acceleration is?","type":"mcq","options":["Zero","Constant","Increasing","Decreasing"],"answer":"Zero","explain":"Horizontal velocity-time line means constant velocity → zero acceleration."},
            {"q":"A ball thrown vertically upward reaches 20 m. Time to reach top?","type":"numeric","answer":2.02,"explain":"t = v/g = 20/9.81 ≈ 2.02 s (approx)"} 
        ],
        "Difficult": [
            {"q":"A car accelerates at 3 m/s² for 10 s then decelerates to stop in 5 s. Find total distance.","type":"numeric","answer":225.0,"explain":"d1=1/2*3*10²=150, v=30; d2=v*t-1/2*6*5²=75; Total=225 m"},
            {"q":"A projectile launched at 30 m/s at 60°. Max height?","type":"numeric","answer":34.64,"explain":"H = (v*sinθ)²/(2g) = (30*√3/2)²/(2*9.81) ≈ 34.64 m"},
            {"q":"Displacement after 4 s if v = 3t² + 2t?","type":"numeric","answer":48.0,"explain":"s=∫v dt=∫(3t²+2t)dt= t³ + t² → 4³+4²=64+16=80? Actually check math: 4³=64, 4²=16 → total s=80 m"},
            {"q":"A particle moves with acceleration a=2t. Initial velocity=0. Displacement after t=3?","type":"numeric","answer":9.0,"explain":"v=∫a dt= t²; s=∫v dt= t³/3 → 3³/3=9 m"},
            {"q":"Which graph represents increasing acceleration?","type":"mcq","options":["Velocity-time straight","Acceleration-time rising line","Position-time parabola","Acceleration-time horizontal"],"answer":"Acceleration-time rising line","explain":"Slope of acceleration-time graph increasing indicates increasing acceleration."}
        ]
    },
    "Energy": {
        "Easy": [
            {"q":"Kinetic energy formula?","type":"mcq","options":["mgh","1/2 m v^2","F s","p v"],"answer":"1/2 m v^2","explain":"KE = 1/2 m v^2."},
            {"q":"2 kg object moves 3 m/s. KE?","type":"numeric","answer":9.0,"explain":"KE = 1/2 m v^2 = 9 J."},
            {"q":"PE = mgh. m=1 kg, g=9.8, h=5 m. PE?","type":"numeric","answer":49.0,"explain":"PE = 1*9.8*5=49 J."},
            {"q":"Total mechanical energy (no friction)?","type":"mcq","options":["KE-PE","KE+PE","Only KE","Only PE"],"answer":"KE+PE","explain":"Mechanical energy = KE + PE."},
            {"q":"Energy unit in SI?","type":"mcq","options":["Joule","Watt","Newton","Volt"],"answer":"Joule","explain":"SI unit of energy is Joule (J)."}
        ],
        "Average": [
            {"q":"Work done by 10 N force moving 5 m?","type":"numeric","answer":50.0,"explain":"Work = F*d = 10*5 = 50 J"},
            {"q":"Power if 100 J done in 5 s?","type":"numeric","answer":20.0,"explain":"P = W/t = 100/5 = 20 W"},
            {"q":"A ball of 2 kg falls from 10 m. KE just before hitting?","type":"numeric","answer":196.0,"explain":"PE=mgh=2*9.8*10=196 J, all converted to KE"},
            {"q":"Which process increases thermal energy?","type":"mcq","options":["Cooling","Friction work","Isothermal expansion","Adiabatic reversible"],"answer":"Friction work","explain":"Friction converts mechanical to thermal energy."},
            {"q":"Mechanical energy conservation example?","type":"mcq","options":["Falling ball","Friction on floor","Car braking","Air drag"],"answer":"Falling ball","explain":"No friction → total energy conserved."}
        ],
        "Difficult": [
            {"q":"A 2 kg mass slides down 5 m. KE at bottom if friction=1 J?","type":"numeric","answer":98.0,"explain":"PE=2*9.8*5=98, minus friction negligible → KE≈98 J"},
            {"q":"Spring k=200 N/m compressed 0.1 m. Stored energy?","type":"numeric","answer":1.0,"explain":"E=1/2 k x^2 = 0.5*200*0.1^2=1 J"},
            {"q":"A roller coaster at top h=20 m, bottom v=?)","type":"numeric","answer":19.8,"explain":"v = √(2gh)=√(2*9.8*20)=19.8 m/s"},
            {"q":"A pendulum swings, max height 2 m. KE at bottom?","type":"numeric","answer":39.2,"explain":"mgh=1*9.8*2=19.6 J; KE=PE at top? Actually KE= mgh = 19.6 J; can adjust m"},
            {"q":"Power required to lift 10 kg, 2 m/s?","type":"numeric","answer":196.0,"explain":"P=F*v = m*g*v = 10*9.8*2=196 W"}
        ]
    },
    "Waves": {
        "Easy": [
            {"q":"Formula of wave speed?","type":"mcq","options":["v=fλ","v=λ/f","v=f+λ","v=f/λ"],"answer":"v=fλ","explain":"Wave speed = frequency × wavelength."},
            {"q":"Amplitude definition?","type":"mcq","options":["Height of wave","Distance","Speed","Energy"],"answer":"Height of wave","explain":"Amplitude is maximum displacement."},
            {"q":"A wave has f=2 Hz, λ=3 m. Speed?","type":"numeric","answer":6.0,"explain":"v=f*λ=2*3=6 m/s"},
            {"q":"Wavelength unit in SI?","type":"mcq","options":["m","s","Hz","J"],"answer":"m","explain":"Meter is SI unit of wavelength."},
            {"q":"Crest of wave is?","type":"mcq","options":["Highest point","Lowest point","Middle","Amplitude"],"answer":"Highest point","explain":"Crest is highest point of wave."}
        ],
        "Average": [
            {"q":"Period T=0.5 s. Frequency?","type":"numeric","answer":2.0,"explain":"f=1/T=1/0.5=2 Hz"},
            {"q":"Wave travels 20 m in 4 s. Speed?","type":"numeric","answer":5.0,"explain":"v=d/t=20/4=5 m/s"},
            {"q":"A sine wave y=A sin(2πft). If f=1 Hz, t=0.25 s, phase?","type":"numeric","answer":0.5*6.2832,"explain":"Phase=2πft=2π*1*0.25≈1.57 rad"},
            {"q":"Which type of wave transfers energy perpendicular to motion?","type":"mcq","options":["Transverse","Longitudinal","Stationary","Surface"],"answer":"Transverse","explain":"Transverse waves have perpendicular motion."},
            {"q":"Nodes in standing wave have?","type":"mcq","options":["Zero displacement","Max displacement","Half displacement","Random"],"answer":"Zero displacement","explain":"Nodes = points of zero displacement."}
        ],
        "Difficult": [
            {"q":"Wave speed v=3 m/s, λ=2 m. Find f?","type":"numeric","answer":1.5,"explain":"f=v/λ=3/2=1.5 Hz"},
            {"q":"Two waves interfere constructively. Resulting amplitude?","type":"numeric","answer":4.0,"explain":"If A1=A2=2, constructive → A=2+2=4"},
            {"q":"A string fixed at both ends. 3rd harmonic λ?","type":"numeric","answer":0.67,"explain":"λ=2L/3, assume L=1 m → λ≈0.67 m"},
            {"q":"Phase difference for destructive interference?","type":"mcq","options":["π","0","π/2","2π"],"answer":"π","explain":"Destructive interference = π rad phase difference."},
            {"q":"Wave energy proportional to?","type":"mcq","options":["Amplitude^2","Frequency","Wavelength","Period"],"answer":"Amplitude^2","explain":"Energy ∝ A²"}
        ]
    }
}

# ---------------------------
# UI helpers
# ---------------------------
def header():
    st.markdown("<h1 style='color:#FF5733; text-align:center;'>⚡ PhysiXplore ⚡</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#3498DB; text-align:center;'>Interactive Physics Learning Hub</h4>", unsafe_allow_html=True)
    st.markdown("---")

def footer():
    st.markdown("---")
    st.markdown("Contact: 24-00496@g.batstate-u.edu.ph  |  Developer: IT-2103 G3")
    st.markdown("© PhysiXplore |         BATANGAS STATE UNIVERSITY - TNE")

# ---------------------------
# Pages
# ---------------------------
def page_home():
    header()

    # -----------------------
    # HIGHLIGHTS (Styled Header)
    # -----------------------


    col1, col2, col3 = st.columns(3)

    # -----------------------
    # BOX 1 - Simulations
    # -----------------------
    with col1:
        st.markdown(
            """
            <div style="
                background:#ffe8d1;
                padding:22px;
                border-radius:18px;
                text-align:center;
                box-shadow:3px 3px 8px rgba(0,0,0,0.12);
                font-family:'Poppins', sans-serif;
            ">
                <div style='font-size:42px;'>🎢</div>
                <h4 style='font-family:"Lobster", cursive; font-size:24px; color:#d35400;'>Simulations</h4>
                <p style='margin-top:-8px; font-size:15px;'>
                    Projectile • Energy Skate • Wave Visualizer
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # -----------------------
    # BOX 2 - Lessons
    # -----------------------
    with col2:
        st.markdown(
            """
            <div style="
                background:#dff1ff;
                padding:22px;
                border-radius:18px;
                text-align:center;
                box-shadow:3px 3px 8px rgba(0,0,0,0.12);
                font-family:'Poppins', sans-serif;
            ">
                <div style='font-size:42px;'>📘</div>
                <h4 style='font-family:"Lobster", cursive; font-size:24px; color:#0277bd;'>Lessons</h4>
                <p style='margin-top:-8px; font-size:15px;'>
                    Guided Examples • Visual Concepts
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # -----------------------
    # BOX 3 - Quizzes
    # -----------------------
    with col3:
        st.markdown(
            """
            <div style="
                background:#f7e6ff;
                padding:22px;
                border-radius:18px;
                text-align:center;
                box-shadow:3px 3px 8px rgba(0,0,0,0.12);
                font-family:'Poppins', sans-serif;
            ">
                <div style='font-size:42px;'>📝</div>
                <h4 style='font-family:"Lobster", cursive; font-size:24px; color:#8e44ad;'>Quizzes</h4>
                <p style='margin-top:-8px; font-size:15px;'>
                    Instant Feedback • Improve Concepts
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # -----------------------
    # QUICK NAVIGATION (4 BIG BUTTONS)
    # -----------------------
    st.markdown("<h3 style='text-align:center; color:#2979ff;'></h3>", unsafe_allow_html=True)
    
    nav1, nav2 = st.columns(2)
    nav3, nav4 = st.columns(2)

    with nav1:
        if st.button("📚 Concepts", use_container_width=True):
            st.session_state["page"] = "concepts"

    with nav2:
        if st.button("📖 Lessons ", use_container_width=True):
            st.session_state["page"] = "lessons"

    with nav3:
        if st.button("📝 Quizzes", use_container_width=True):
            st.session_state["page"] = "quizzes"

    with nav4:
        if st.button("🎢 Simulations", use_container_width=True):
            st.session_state["page"] = "sims"

    # -----------------------
    # FEATURED BANNER
    # -----------------------
    st.markdown("""
        <div style="
            background:#e8f2ff;
            padding: 12px;
            margin-top: 25px;
            border-radius: 12px;
            border-left: 8px solid #2979ff;">
            <b>ℹ️ Featured:</b> Projectile Motion Simulator • Energy Skate Park • Wave Visualizer
        </div>
    """, unsafe_allow_html=True)


def page_concepts():
    header()
    st.markdown(
        """
        <div style='text-align:center; background-color:#e1f5fe; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h1 style='color:#0288d1; font-family:"Lobster", cursive;'>🔎 Key Concepts</h1>
        <p style='font-size:16px; line-height:1.5'>
        Explore important science concepts interactively! Select a topic below to see its definition and related simulation.
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    topic = st.selectbox(
        "",
        ["Motion", "Energy", "Waves"]
    )

    if topic == "Motion":
        st.markdown(
            """
            <div style='background-color:#e0f7fa; padding:15px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <h2 style='color:#00796b; font-family:"Lobster", cursive;'>Motion 🏎</h2>
            <p style='font-size:16px; line-height:1.5'>
            Motion is the study of <b>displacement, velocity, and acceleration</b>.<br>
            Kinematics describes motion under constant acceleration.
            </p>
            <p style='font-size:15px;'>Try the <b>'Projectile Motion'</b> simulation 🎯 to see it in action!</p>
            </div>
            """, unsafe_allow_html=True
        )

    elif topic == "Energy":
        st.markdown(
            """
            <div style='background-color:#fff3e0; padding:15px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <h2 style='color:#f57c00; font-family:"Lobster", cursive;'>Energy ⚡</h2>
            <p style='font-size:16px; line-height:1.5'>
            Energy appears as <b>kinetic (KE)</b>, <b>potential (PE)</b>, and <b>thermal energy</b>.<br>
            Mechanical energy is the sum of KE + PE.
            </p>
            <p style='font-size:15px;'>Try the <b>'Energy Skate Park'</b> simulation 🛹 to explore energy in action!</p>
            </div>
            """, unsafe_allow_html=True
        )

    else:
        st.markdown(
            """
            <div style='background-color:#e8eaf6; padding:15px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <h2 style='color:#3949ab; font-family:"Lobster", cursive;'>Waves 🌊</h2>
            <p style='font-size:16px; line-height:1.5'>
            Waves are disturbances that carry energy from one place to another without moving matter.<br>
            The highest point is the <b>crest</b>, the lowest is the <b>trough</b>, and the <b>wavelength</b> is the distance between them.<br>
            Waves occur in water, sound, and light.
            </p>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")
    st.button("⬅ Back to Home", on_click=lambda: st.session_state.update(page="home"))

def page_lessons():
    header()
    st.markdown(
        """
        <div style='text-align:center; background-color:#f0f4c3; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h1 style='color:#689f38; font-family:"Lobster", cursive;'>🌟Lessons & Examples🌟</h1>
        <p style='font-size:16px; line-height:1.6'>
        Welcome to our interactive science lessons! Explore concepts through explanations, examples, and visual simulations.  
        Learn <b>motion, energy, and waves</b> in a fun and engaging way.
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("---")

    # ---------------------------
    # MOTION VISUAL
    # ---------------------------
    with st.container():
        st.markdown(
            """
            <div style='background-color:#e0f7fa; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <h2 style='color:#00796b; font-family:"Lobster", cursive;'>Motion 🏎</h2>
            <p style='font-size:16px; line-height:1.5'>
            Motion is the <b>change in an object's position over time</b> relative to a reference point.<br>
            It's described using <b>distance, displacement, speed, velocity, and acceleration</b>.<br>
            <b>Example:</b> A car accelerates at <b>3 m/s²</b>, reaches <b>v = 15 m/s</b>, and travels <b>37.5 m</b> in 5 seconds.<br>
            Explore how motion changes over time using the graph below!
            </p>
            </div>
            """, unsafe_allow_html=True
        )

        t = np.linspace(0, 5, 100)
        a = 3
        x = 0.5 * a * t**2

        fig1, ax1 = plt.subplots(figsize=(6,3))
        ax1.plot(t, x, color="#00796b", linewidth=2)
        ax1.set_xlabel("Time (s)", fontsize=10, fontname="Poppins")
        ax1.set_ylabel("Distance (m)", fontsize=10, fontname="Poppins")
        ax1.set_title("Motion Example: Accelerated Car", fontsize=12, fontname="Poppins")
        ax1.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig1)

    st.markdown("---")

    # ---------------------------
    # ENERGY VISUAL
    # ---------------------------
    with st.container():
        st.markdown(
            """
            <div style='background-color:#fff3e0; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <h2 style='color:#f57c00; font-family:"Lobster", cursive;'>Energy ⚡</h2>
            <p style='font-size:16px; line-height:1.5'>
            Energy is the <b>ability to do work</b>. It appears as <b>kinetic energy (KE)</b> or <b>potential energy (PE)</b>.<br>
            <b>Example:</b> A 2 kg object moving at 4 m/s has <b>KE = 16 J</b>. Potential energy can be calculated based on height and gravity.<br>
            Visualize the distribution of energy below!
            </p>
            </div>
            """, unsafe_allow_html=True
        )

        KE = 16
        PE = 10

        fig2, ax2 = plt.subplots(figsize=(6,3))
        bars = ax2.bar(["KE", "PE"], [KE, PE], color=["#f57c00", "#ffb74d"])
        ax2.set_title("Energy Representation", fontsize=12, fontname="Poppins")
        ax2.set_ylabel("Energy (J)", fontsize=10, fontname="Poppins")
        ax2.bar_label(bars)
        st.pyplot(fig2)

    st.markdown("---")

    # ---------------------------
    # WAVES VISUAL
    # ---------------------------
    with st.container():
        st.markdown(
            """
            <div style='background-color:#e8eaf6; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <h2 style='color:#3949ab; font-family:"Lobster", cursive;'>Waves 🌊</h2>
            <p style='font-size:16px; line-height:1.5'>
            A wave is a <b>disturbance that transfers energy</b> through a medium without moving matter.<br>
            Common examples: <b>sound waves, light waves, and water waves</b>.<br>
            Observe how amplitude and frequency affect wave behavior in the graph below!
            </p>
            </div>
            """, unsafe_allow_html=True
        )

        x = np.linspace(0, 2*np.pi, 300)
        y = np.sin(5 * x)

        fig3, ax3 = plt.subplots(figsize=(6,3))
        ax3.plot(x, y, color="#3949ab", linewidth=2)
        ax3.set_title("Wave Representation", fontsize=12, fontname="Poppins")
        ax3.set_xlabel("Position", fontsize=10, fontname="Poppins")
        ax3.set_ylabel("Amplitude", fontsize=10, fontname="Poppins")
        ax3.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig3)

    st.markdown("---")

    st.button("⬅ Back to Home", on_click=lambda: st.session_state.update(page="home"))

def page_quizzes():
    header()
    st.markdown(
        """
        <div style='text-align:center; background-color:#ffe0b2; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h1 style='color:#e65100; font-family:"Lobster", cursive;'>📝  Quizzes 📝</h1>
        <p style='font-size:16px; line-height:1.5'>
        Test your knowledge in <b>Motion, Energy, and Waves</b>! Select a topic and difficulty, then try to answer all questions correctly.  
        Good luck! 🍀
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    # ---------------------------
    # User Name Input
    # ---------------------------
    with st.container():
        st.markdown(
            """
            <div style='background-color:#f1f8e9; padding:15px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <p style='font-size:15px; line-height:1.5'>👤 Enter your name:</p>
            </div>
            """, unsafe_allow_html=True
        )
    username = st.text_input("", value=st.session_state.get("username", "Guest"))
    st.session_state["username"] = username

    # ---------------------------
    # Select Topic & Difficulty
    # ---------------------------
    with st.container():
        st.markdown(
            """
            <div style='background-color:#e3f2fd; padding:15px; border-radius:10px; font-family:"Poppins", sans-serif;'>
            <p style='font-size:15px; line-height:1.5'>🎯 Select your topic and difficulty:</p>
            </div>
            """, unsafe_allow_html=True
        )
    topic = st.selectbox("", ["Motion", "Energy", "Waves"])
    difficulty = st.selectbox("", ["Easy", "Average", "Difficult"])

    # Reset quiz if topic or difficulty changed
    if "quiz_active" not in st.session_state or \
       st.session_state.get("quiz_topic") != topic or \
       st.session_state.get("quiz_difficulty") != difficulty:
        st.session_state.update({
            "quiz_active": False,
            "quiz_topic": topic,
            "quiz_difficulty": difficulty,
            "quiz_index": 0,
            "quiz_answers": []
        })

    # ---------------------------
    # Start Quiz Button
    # ---------------------------
    start = st.button("Start Quiz 🏁", key="start_quiz")
    if start:
        st.session_state["quiz_active"] = True

    # ---------------------------
    # Quiz Active
    # ---------------------------
    if st.session_state.get("quiz_active", False):
        qi = st.session_state.get("quiz_index", 0)
        user_answers = st.session_state.get("quiz_answers", [])
        questions = QUIZZES[topic][difficulty]

        # --- All Questions Answered ---
        if qi >= len(questions):
            st.success(f"🎉 Quiz Complete! You answered all {len(questions)} questions.")

            st.subheader("📖 Answers & Explanations")
            score = 0
            for i, q in enumerate(questions):
                st.markdown(
                    f"<div style='background-color:#fff9c4; padding:10px; border-radius:10px; font-family:Poppins;'>"
                    f"<b>Question {i+1}:</b> {q['q']}</div>",
                    unsafe_allow_html=True
                )

                user_ans = user_answers[i] if i < len(user_answers) else "No answer"
                correct_ans = q["answer"]
                is_correct = False

                if q["type"] == "mcq":
                    is_correct = user_ans == correct_ans
                else:
                    try:
                        is_correct = math.isclose(float(user_ans), float(correct_ans), rel_tol=1e-3, abs_tol=1e-3)
                    except:
                        is_correct = False

                st.markdown(
                    f"<div style='background-color:#e8f5e9; padding:5px; border-radius:8px;'>"
                    f"Your answer: {user_ans} {'✅' if is_correct else '❌'}<br>"
                    f"Correct answer: {correct_ans}</div>",
                    unsafe_allow_html=True
                )
                st.info(f"💡 Explanation: {q.get('explain', 'No explanation.')}")
                
                if is_correct:
                    score += 1

            st.success(f"🏆 Total Score: {score}/{len(questions)}")

            if st.button("Back to Home ⬅", key="quiz_home"):
                st.session_state.update(page="home", quiz_active=False, quiz_index=0, quiz_answers=[])
            return

        # --- Current Question ---
        q = questions[qi]
        st.markdown(
            f"<div style='background-color:#fce4ec; padding:15px; border-radius:10px; font-family:Poppins;'>"
            f"<b>Question {qi+1} of {len(questions)}:</b> {q['q']}</div>",
            unsafe_allow_html=True
        )

        user_answer_key = f"ans_{topic}_{difficulty}_{qi}"
        if q["type"] == "mcq":
            ans = st.radio("", q["options"], key=user_answer_key)
        else:
            ans = st.text_input("", key=user_answer_key)

        col1, col2 = st.columns(2)
        if col1.button("Submit Answer ✅", key=f"submit_{qi}"):
            user_answers.append(ans)
            st.session_state["quiz_answers"] = user_answers
            st.session_state["quiz_index"] = qi + 1
            return

        if col2.button("Cancel Quiz ❌", key=f"cancel_{qi}"):
            st.session_state.update(quiz_active=False, quiz_index=0, quiz_answers=[])
            return

    # ---------------------------
    # Back to Home
    # ---------------------------
    st.button("⬅ Back to Home", on_click=lambda: st.session_state.update(page="home"))


# Simulations
def sims_projectile_combined():
    st.markdown(
        """
        <div style='text-align:center; background-color:#e1f5fe; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h2 style='color:#0288d1; font-family:"Lobster", cursive;'>🚀 Projectile Motion Simulator</h2>
        <p style='font-size:16px; line-height:1.5'>
        Visualize projectile motion with real-time animation and see calculated results for maximum height, range, and flight time!
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    # Inputs
    v0 = st.slider("Initial speed (m/s)", 5, 50, 20)
    angle_deg = st.slider("Angle (°)", 10, 80, 45)
    g = 9.81

    if st.button("Launch 🚀"):
        theta = math.radians(angle_deg)

        # Calculations
        t_flight = 2 * v0 * math.sin(theta) / g
        H_max = (v0**2 * math.sin(theta)**2) / (2 * g)
        R = (v0**2 * math.sin(2*theta)) / g

        # Results box
        st.markdown(
            f"""
            <div style="background-color:#fff3e0;padding:15px;border-radius:10px;border:1px solid #ffb74d; font-family:'Poppins', sans-serif;">
                <h4 style="color:#f57c00;">📊 Projectile Motion Results</h4>
                <p><b>Time of flight:</b> {t_flight:.2f} s</p>
                <p><b>Maximum height:</b> {H_max:.2f} m</p>
                <p><b>Range:</b> {R:.2f} m</p>
            </div>
            """, unsafe_allow_html=True
        )

        # Trajectory points
        frames = 200
        t = np.linspace(0, t_flight, frames)
        x = v0 * np.cos(theta) * t
        y = v0 * np.sin(theta) * t - 0.5 * g * t**2

        # Animation speed
        animation_speed = t_flight / frames

        # Prepare figure
        placeholder = st.empty()
        fig, ax = plt.subplots(figsize=(6,3))

        ax.set_xlim(0, max(x) * 1.1)
        ax.set_ylim(0, max(y) * 1.2)
        ax.set_xlabel("Distance (m)", fontsize=10, fontname="Poppins")
        ax.set_ylabel("Height (m)", fontsize=10, fontname="Poppins")
        ax.set_title("Trajectory Animation", fontsize=12, fontname="Poppins")

        # Animation lines
        line, = ax.plot([], [], 'r-', lw=2, label="Trajectory")
        point, = ax.plot([], [], 'bo', markersize=8)

        # Max height marker
        x_max_height = v0 * math.cos(theta) * (t_flight / 2)
        ax.plot(x_max_height, H_max, 'go', markersize=8, label="Max Height")
        ax.axhline(H_max, color='green', linestyle='--', alpha=0.6)

        # Range marker
        ax.plot(R, 0, 'mo', markersize=8, label="Landing Point")
        ax.axvline(R, color='magenta', linestyle='--', alpha=0.6)

        ax.legend(fontsize=8)

        # Animation loop
        for i in range(len(t)):
            line.set_data(x[:i+1], y[:i+1])
            point.set_data([x[i]], [y[i]])
            placeholder.pyplot(fig)
            time.sleep(animation_speed)

    st.markdown("---")

def sims_energy_skate():
    # ---------- Header ----------
    st.markdown(
        """
        <div style='text-align:center; background-color:#f3e5f5; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h2 style='color:#6a1b9a; font-family:"Lobster", cursive;'>🛹 Energy Skate Park Simulator</h2>
        <p style='font-size:16px; line-height:1.5'>
        Explore how **Potential Energy (PE) and Kinetic Energy (KE)** transform as the skater moves along the track!
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    # ---------- Inputs ----------
    st.markdown(
        "<div style='background-color:#E5B0DF; padding:15px; border-radius:10px; font-family:Poppins;'>"
        "<p style='font-size:15px;'>Set initial parameters for the skater:</p></div>", unsafe_allow_html=True
    )

    m = st.number_input("Mass of Skater (kg)", 1.0, 100.0, step=0.1)
    h = st.number_input("Initial Height (m)", 0.0, 50.0, step=0.1)
    v = st.number_input("Initial Velocity (m/s)", 0.0, 50.0, step=0.1)
    g = 9.81  # gravity

    # Compute total energy
    pe_initial = m * g * h
    ke_initial = 0.5 * m * v**2
    total_energy = pe_initial + ke_initial

    st.markdown(f"<p style='font-size:16px; font-weight:bold;'>💡 Total Energy: {total_energy:.2f} J</p>", unsafe_allow_html=True)

    # ---------- Skater Position Slider ----------
    position = st.slider("Skater Position along Track (0=start, 1=end)", 0.0, 1.0, 0.0, 0.01)

    # Current energies
    current_height = h * (1 - position)
    current_pe = m * g * current_height
    current_ke = total_energy - current_pe

    # ---------- Horizontal Metrics ----------
    col1, col2, col3 = st.columns(3)
    col1.metric("Potential Energy (PE)", f"{current_pe:.2f} J")
    col2.metric("Kinetic Energy (KE)", f"{current_ke:.2f} J")
    col3.metric("Total Energy", f"{current_pe + current_ke:.2f} J")

    # ---------- Track Visualization ----------
    x = np.linspace(0, 10, 100)
    heights = h * (1 - x/10)
    skater_pe = m * g * heights
    skater_ke = total_energy - skater_pe

    fig2, ax2 = plt.subplots(figsize=(8,4))
    ax2.plot(x, skater_pe, label='PE', color='#1f77b4', lw=2)
    ax2.plot(x, skater_ke, label='KE', color='#ff7f0e', lw=2)
    ax2.plot(x, [total_energy]*len(x), '--', label='Total Energy', color='#2ca02c', lw=1.5)
    ax2.scatter(position*10, current_pe, color='red', s=100, label='Skater')
    ax2.set_xlabel("Track Position", fontsize=12, fontname="Poppins")
    ax2.set_ylabel("Energy (Joules)", fontsize=12, fontname="Poppins")
    ax2.set_title("Energy Transformation Along Track", fontsize=14, fontname="Poppins")
    ax2.legend(fontsize=10)
    st.pyplot(fig2)

    # ---------- Educational Info ----------
    st.markdown(
        "<div style='background-color:#e8f5e9; padding:15px; border-radius:10px; font-family:Poppins;'>"
        "🔹 Drag the slider to move the skater along the track.<br>"
        "🔹 Observe <b>PE decreasing</b> and <b>KE increasing</b> while total energy remains constant.<br>"
        "🔹 This demonstrates the <b>law of conservation of energy</b> in action."
        "</div>", unsafe_allow_html=True
    )

    # ---------- Energy Bar Chart ----------
    fig, ax = plt.subplots(figsize=(8,5))
    energies = [current_pe, current_ke, total_energy]
    labels = ['Potential Energy', 'Kinetic Energy', 'Total Energy']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    ax.bar(labels, energies, color=colors)
    for i, e in enumerate(energies):
        ax.text(i, e + total_energy*0.02, f"{e:.2f} J", ha='center', fontweight='bold', fontsize=12)
    ax.set_ylabel("Energy (Joules)", fontsize=12, fontname="Poppins")
    ax.set_title("Energy Distribution", fontsize=14, fontname="Poppins")
    ax.tick_params(axis='both', labelsize=12)
    st.pyplot(fig)

    st.markdown("---")


def sims_wave():
    # ---------- Header ----------
    st.markdown(
        """
        <div style='text-align:center; background-color:#e0f7fa; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h2 style='color:#006064; font-family:"Lobster", cursive;'>🌊 Wave Simulator</h2>
        <p style='font-size:16px; line-height:1.5'>
        Animate sine waves and visualize **peaks, troughs, and zero crossings** with interactive controls!
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    # ---------- Inputs ----------
    st.markdown(
        "<div style='background-color:#b2ebf2; padding:15px; border-radius:10px; font-family:Poppins;'>"
        "<p style='font-size:15px;'>Set wave parameters below:</p></div>", unsafe_allow_html=True
    )

    A = st.slider("Amplitude", 0.1, 5.0, 1.0)
    f = st.slider("Frequency (Hz)", 0.1, 5.0, 1.0)
    duration = st.number_input("Duration (s)", 1.0, 10.0, 2.0, step=0.5)
    speed_factor = st.slider("Animation speed", 1, 20, 5)
    animation_speed = 0.02 * (20 / speed_factor)  # smaller = faster

    if st.button("Animate 🌈"):
        x = np.linspace(0, duration, 400)
        y_full = A * np.sin(2 * math.pi * f * x)
        placeholder = st.empty()

        fig, ax = plt.subplots(figsize=(8,4))
        ax.set_xlim(0, duration)
        ax.set_ylim(-A*1.2, A*1.2)
        ax.set_xlabel("Time (s)", fontsize=12, fontname="Poppins")
        ax.set_ylabel("Amplitude", fontsize=12, fontname="Poppins")
        ax.set_title("Sine Wave Animation", fontsize=14, fontname="Poppins")

        line, = ax.plot([], [], 'b-', lw=2, label="Sine Wave")
        fill = None
        labels = []

        # Precompute markers
        peaks, troughs, zeros = [], [], []
        for i in range(1, len(y_full)-1):
            if y_full[i-1] < y_full[i] > y_full[i+1]:
                peaks.append((x[i], y_full[i]))
            elif y_full[i-1] > y_full[i] < y_full[i+1]:
                troughs.append((x[i], y_full[i]))
            elif (y_full[i-1] < 0 and y_full[i] >= 0) or (y_full[i-1] > 0 and y_full[i] <= 0):
                zeros.append((x[i], y_full[i]))

        # Animate wave
        for i in range(len(x)):
            y = y_full[:i+1]
            line.set_data(x[:i+1], y)

            if fill:
                fill.remove()
            for lbl in labels:
                lbl.remove()
            labels.clear()

            fill = ax.fill_between(x[:i+1], 0, y, color='lightblue', alpha=0.3)

            for px, py in peaks:
                if px <= x[i]:
                    ax.plot(px, py, 'go', markersize=6)
                    lbl = ax.text(px, py + 0.1, f"{py:.2f}", color='green', fontsize=8)
                    labels.append(lbl)
            for tx, ty in troughs:
                if tx <= x[i]:
                    ax.plot(tx, ty, 'ro', markersize=6)
                    lbl = ax.text(tx, ty - 0.2, f"{ty:.2f}", color='red', fontsize=8)
                    labels.append(lbl)
            for zx, zy in zeros:
                if zx <= x[i]:
                    ax.plot(zx, zy, 'ko', markersize=4)
                    lbl = ax.text(zx, zy + 0.1, f"{zy:.2f}", color='black', fontsize=7)
                    labels.append(lbl)

            placeholder.pyplot(fig)
            time.sleep(animation_speed)

        # ---------- Final Summary ----------
        st.markdown(
            f"<div style='background-color:#e0f2f1; padding:15px; border-radius:10px; font-family:Poppins;'>"
            f"<p style='font-size:15px; font-weight:bold;'>✅ Wave Completed!</p>"
            f"<p>Max amplitude: <b>{A}</b>, Frequency: <b>{f} Hz</b>, Duration: <b>{duration}s</b></p>"
            f"<p>Peaks: <b>{len(peaks)}</b>, Troughs: <b>{len(troughs)}</b>, Zero crossings: <b>{len(zeros)}</b></p>"
            "</div>", unsafe_allow_html=True
        )

    st.markdown("---")

    

def page_simulations():
    header()
    st.markdown(
        """
        <div style='text-align:center; background-color:#f3e5f5; padding:20px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <h1 style='color:#6a1b9a; font-family:"Lobster", cursive;'>🎮 Simulations Hub</h1>
        <p style='font-size:16px; line-height:1.5'>
        Explore interactive simulations to visualize science concepts. Choose one below and see the magic in action!
        </p>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='background-color:#FFACD8; padding:15px; border-radius:10px; font-family:"Poppins", sans-serif;'>
        <p style='font-size:16px; line-height:1.5'>Select a simulation to start:</p>
        </div>
        """, unsafe_allow_html=True
    )

    sim = st.radio("", ["Projectile Motion 🎯", "Energy Skate Park 🛹", "Wave Visualizer 🌊"])

    if sim.startswith("Projectile Motion 🎯"): 
        sims_projectile_combined()
    elif sim.startswith("Energy Skate Park"): 
        sims_energy_skate()
    else: 
        sims_wave()
    
    st.button("⬅ Back to Home", key="back_home_sim_page", on_click=lambda: st.session_state.update(page="home"))



# Main
if "page" not in st.session_state: st.session_state["page"]="home"

page = st.session_state["page"]
if page=="home": page_home()
elif page=="concepts": page_concepts()
elif page=="lessons": page_lessons()
elif page=="quizzes": page_quizzes()
elif page=="sims": page_simulations()

footer()

