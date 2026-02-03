"""
MV Del Monte Loadicator - Streamlit Web Application
Stability Calculator and GZ Curve Generator
"""

import streamlit as st
import matplotlib.pyplot as plt
from data_loader import DataLoader
from interpolation import Interpolator
from calculator import StabilityCalculator
from visualizer import Visualizer

# Page configuration
st.set_page_config(
    page_title="MV Del Monte Loadicator",
    page_icon="ship",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_data():
    """Load and cache vessel data from embedded sources"""
    loader = DataLoader(use_embedded=True)
    loader.load_hydrostatic_data()
    loader.load_kn_curves()
    loader.validate_data()
    return loader


def main():
    # Header
    st.title("MV Del Monte Loadicator")
    st.markdown("**Stability Calculator and GZ Curve Generator**")
    st.markdown("*Emergency backup tool for stability verification when loading computer fails*")
    st.divider()

    # Load data
    try:
        loader = load_data()
        interpolator = Interpolator(loader)
        calculator = StabilityCalculator(interpolator)
        visualizer = Visualizer()
    except Exception as e:
        st.error(f"Error loading vessel data: {e}")
        return

    # Get valid ranges
    draft_min, draft_max = loader.get_draft_range()
    disp_min, disp_max = loader.get_displacement_range()

    # Sidebar with vessel info
    with st.sidebar:
        st.header("Vessel Information")
        st.markdown("""
        **MV Del Monte**
        - Length Overall: 223.00 m
        - Length BP: 216.00 m
        - Summer Draft: 13.02 m
        - Summer Displacement: 77,165 t
        - Deadweight: 66,612 t
        """)

        st.divider()

        st.header("Valid Input Ranges")
        st.markdown(f"""
        - **Draft**: {draft_min:.2f}m to {draft_max:.2f}m
        - **Displacement**: {disp_min:,.0f}t to {disp_max:,.0f}t
        """)

        st.divider()

        with st.expander("Technical Notes"):
            st.markdown("""
            **About the GZ Curve at High Angles:**

            The KN cross-curve data at angles above 60 degrees may show GZ
            remaining positive. For most vessels, GZ typically becomes
            negative between 60-80 degrees.

            This is due to the theoretical nature of the cross-curve data
            which may not fully account for deck edge immersion at extreme
            heel angles.

            **The IMO stability criteria (evaluated up to 40 degrees) remain
            fully accurate and valid.**

            **Formula used:**
            - GZ = KN - KG x sin(heel angle)
            - GM = KM - KG
            - KM = KB + BM (metacentric radius)
            """)

    # Main input section
    st.header("Input Parameters")

    col1, col2 = st.columns(2)

    with col1:
        draft = st.number_input(
            "Draft at Perpendiculars (m)",
            min_value=float(draft_min),
            max_value=float(draft_max),
            value=10.0,
            step=0.01,
            format="%.2f",
            help=f"Enter draft between {draft_min:.2f}m and {draft_max:.2f}m"
        )

    with col2:
        kg = st.number_input(
            "KG - Vertical Center of Gravity (m)",
            min_value=0.1,
            max_value=15.0,
            value=8.5,
            step=0.01,
            format="%.2f",
            help="Enter the vertical center of gravity from keel"
        )

    st.divider()

    # Calculate button
    if st.button("Calculate Stability", type="primary", use_container_width=True):
        try:
            with st.spinner("Calculating stability parameters..."):
                results = calculator.calculate_stability(draft, kg)

            # Store results in session state
            st.session_state['results'] = results
            st.session_state['draft'] = draft
            st.session_state['kg'] = kg

        except ValueError as e:
            st.error(f"Calculation Error: {e}")
            return
        except Exception as e:
            st.error(f"Unexpected Error: {e}")
            return

    # Display results if available
    if 'results' in st.session_state:
        results = st.session_state['results']
        draft = st.session_state['draft']
        kg = st.session_state['kg']

        # Key metrics
        st.header("Stability Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Displacement",
                f"{results['stability']['displacement']:,.0f} t"
            )

        with col2:
            gm = results['stability']['gm']
            st.metric(
                "GM (Metacentric Height)",
                f"{gm:.3f} m",
                delta="OK" if gm >= 0.15 else "LOW"
            )

        with col3:
            st.metric(
                "Maximum GZ",
                f"{results['stability']['max_gz']:.3f} m",
                delta=f"at {results['stability']['angle_at_max_gz']:.1f} deg"
            )

        with col4:
            compliance = results['compliance']['overall']
            if compliance['pass']:
                st.metric("IMO Status", "COMPLIANT")
            else:
                st.metric("IMO Status", "NON-COMPLIANT")

        st.divider()

        # Additional parameters
        st.subheader("Hydrostatic Parameters")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("KB", f"{results['stability']['kb']:.3f} m")
        with col2:
            st.metric("KM", f"{results['stability']['km']:.3f} m")
        with col3:
            vanishing = results['stability']['vanishing_angle']
            if vanishing:
                st.metric("Vanishing Angle", f"{vanishing:.1f} deg")
            else:
                st.metric("Vanishing Angle", "Not found")
        with col4:
            st.metric("GZ at 30 deg", f"{results['stability']['gz_at_30']:.3f} m")

        # Warning for vanishing angle
        if results['stability']['vanishing_angle'] is None:
            st.warning(
                "**Note:** Vanishing angle not found within data range (0-90 degrees). "
                "GZ remains positive at all calculated heel angles. "
                "This is a known limitation of the KN curve data at high angles. "
                "**The IMO stability criteria (evaluated up to 40 degrees) remain fully valid.**"
            )

        st.divider()

        # GZ Curve Plot
        st.subheader("GZ Curve (Righting Lever)")

        fig = visualizer.plot_gz_curve(results, show_plot=False)
        st.pyplot(fig)
        plt.close(fig)

        st.divider()

        # IMO Compliance Details
        st.subheader("IMO Intact Stability Code Compliance")

        compliance = results['compliance']

        # Create compliance table
        criteria_data = []
        for key, criterion in compliance.items():
            if key == 'overall':
                continue
            criteria_data.append({
                'Criterion': criterion['requirement'],
                'Actual Value': f"{criterion['value']:.4f}",
                'Required': f">= {criterion['limit']}",
                'Status': criterion['status']
            })

        # Display with color coding
        for item in criteria_data:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(item['Criterion'])
            with col2:
                st.write(item['Actual Value'])
            with col3:
                st.write(item['Required'])
            with col4:
                if item['Status'] == 'PASS':
                    st.success(item['Status'])
                else:
                    st.error(item['Status'])

        # Overall status
        st.divider()
        if compliance['overall']['pass']:
            st.success("**OVERALL: VESSEL MEETS ALL IMO INTACT STABILITY CODE REQUIREMENTS**")
        else:
            st.error("**OVERALL: VESSEL DOES NOT MEET ALL IMO REQUIREMENTS - REVIEW LOADING CONDITION**")

        st.divider()

        # GZ Curve Data Table
        with st.expander("View GZ Curve Data Table"):
            gz_curve = results['gz_curve']
            import pandas as pd
            gz_df = pd.DataFrame({
                'Heel Angle (deg)': gz_curve['heel_angles'],
                'KN (m)': [f"{kn:.3f}" for kn in gz_curve['kn_values']],
                'GZ (m)': [f"{gz:.3f}" for gz in gz_curve['gz_values']]
            })
            st.dataframe(gz_df, use_container_width=True)

        # Download section
        st.divider()
        st.subheader("Export Report")

        col1, col2 = st.columns(2)

        with col1:
            # PDF Download
            pdf_bytes = visualizer.export_to_pdf_bytes(results)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"stability_report_draft{draft:.2f}_kg{kg:.2f}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col2:
            # Text report
            text_report = calculator.generate_report(results)
            st.download_button(
                label="Download Text Report",
                data=text_report,
                file_name=f"stability_report_draft{draft:.2f}_kg{kg:.2f}.txt",
                mime="text/plain",
                use_container_width=True
            )

    # Footer
    st.divider()
    st.caption(
        "MV Del Monte Loadicator v1.0 | "
        "Emergency stability verification tool | "
        "For use when approved loading computer has failed"
    )


if __name__ == "__main__":
    main()
