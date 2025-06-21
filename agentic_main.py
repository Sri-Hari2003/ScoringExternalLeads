from data_collectors.agentic_intent_analyzer import run_agentic_analysis, create_ai_dashboard
from main import run_enhanced_intent_signal_collection
import os

if __name__ == "__main__":
    # Run the main pipeline to collect signals and get the output directory
    collector, analyzer, comprehensive_df = run_enhanced_intent_signal_collection()
    output_dir = analyzer.output_dir

    # Run the agentic analysis
    agentic_processor, ai_recommendations = run_agentic_analysis(collector, output_dir)

    # Create AI dashboard
    create_ai_dashboard(output_dir)

    print(f"\n🎉 AGENTIC ANALYSIS COMPLETED!")
    print(f"📁 AI-Enhanced files generated in: {output_dir}")
    print(f"  • ai_enhanced_intent_signals.csv - Complete AI analysis")
    print(f"  • immediate_action_signals.csv - Urgent follow-ups")
    print(f"  • high_priority_queue.csv - Priority prospects")
    print(f"\n🤖 The AI agent has analyzed your signals and made autonomous recommendations!")
    print(f"💡 Check the immediate action items for urgent follow-ups!") 