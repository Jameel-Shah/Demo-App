import streamlit as st
# title
st.title("Welcome to Corvit HCCDA-AI")
# write
st.write("We are learning UV Platform")
# header
st.header("This is header")
# subheader
st.subheader("This is subheader")
# markdown
st.markdown("#### 4th heading")
# text
st.text(2)
# write
st.write(2)

st.success("Registeration Successful")
st.info("For more information")
# error
st.error("Error")
# warnig
st.warning("Warning")
# Image
st.image("W(1).jpg")
# Check-box
if st.checkbox("Male"):
    st.text("You are male")

if st.checkbox("Female"):
    st.text("You are Female")

# Radio-button
status= st.radio("Select Gender: ", ('Male', 'Female'))
if status == 'Male':
    st.success("You are brave..")
else:
    st.success("You are kind lady...")

# Dropdown
hobby= st.selectbox("Hobbies: ", ['Dancing', 'Reading', 'Sports'])
# print the slected hobby
st.write("Your hobby is:", hobby)
# Dropdown Multiple
hobbies= st.multiselect("Hobbies: ", ['Dancing', 'Reading', 'Sports'])
st.write("You selected", len(hobbies), hobbies, 'hobbies')

if st.button("Click me", type= "primary"):
    st.write("Hello")

level= st.slider("Select the level:", 1,10)