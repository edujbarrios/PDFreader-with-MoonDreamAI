import streamlit as st
from utils import validate_api_key, extract_first_page_as_image, analyze_image_with_moondream

def initialize_session_state():
    """Initialize session state variables."""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None

def format_analysis_result(result: str) -> str:
    """Format the analysis result for better display."""
    sections = result.split('\n\n')
    formatted_sections = []
    for section in sections:
        if ':' in section:
            title, content = section.split(':', 1)
            formatted_sections.append(f"### {title.strip()}\n{content.strip()}")
        else:
            formatted_sections.append(section)
    return '\n\n'.join(formatted_sections)

def main():
    st.set_page_config(
        page_title="PDFreader with MoonDream",
        page_icon="📄",
        layout="wide"
    )

    initialize_session_state()

    st.title("📄 PDFreader with MoonDream")
    st.markdown("---")

    # API Key Input Section
    with st.expander("🔑 API Key Configuration", expanded=not bool(st.session_state.api_key)):
        api_key_input = st.text_input(
            "Enter your Moondream API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your Moondream API key to start analyzing PDF cover pages"
        )

        if api_key_input:
            if validate_api_key(api_key_input):
                st.session_state.api_key = api_key_input
                st.success("API Key saved successfully!")
            else:
                st.error("Invalid API Key format. Please check and try again.")

    # Main Application Section
    if st.session_state.api_key:
        st.markdown("### Upload PDF Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF file to analyze its cover page"
        )

        if uploaded_file:
            col1, col2 = st.columns([1, 1])

            with col1:
                with st.spinner("Processing PDF..."):
                    # Extract first page as image
                    pdf_bytes = uploaded_file.read()
                    image_bytes = extract_first_page_as_image(pdf_bytes)

                    if image_bytes:
                        # Display the extracted cover page
                        st.markdown("### Cover Page Preview")
                        st.image(image_bytes, caption="Extracted Cover Page", use_container_width=True)

                        # Analyze button
                        if st.button("🔍 Analyze Cover Page"):
                            with st.spinner("Analyzing cover page with Moondream API..."):
                                success, result = analyze_image_with_moondream(
                                    st.session_state.api_key,
                                    image_bytes
                                )

                                if success:
                                    st.session_state.analysis_result = result
                                else:
                                    st.error(result)
                    else:
                        st.error("Failed to extract the cover page from the PDF. Please try another file.")

            with col2:
                if st.session_state.analysis_result:
                    st.markdown("### Analysis Results")
                    st.markdown(format_analysis_result(st.session_state.analysis_result))
    else:
        st.info("Please configure your Moondream API key to start analyzing PDF cover pages.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ by <a href="https://edujbarrios.com" target="_blank">Eduardo Jose Barrios Garcia</a> (@edujbarrios)</p>
            <p>Using Streamlit and Moondream API</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()