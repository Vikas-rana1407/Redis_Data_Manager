from typing import Optional

def prepare_prompt(
    transcript_text: str,
    video_title: str,
    video_id: str,
    activity_tags: str,
    goal_objective_tags: Optional[str] = None,
    edited_prompt: Optional[str] = None,
):
    if edited_prompt:
        return edited_prompt

    return f"""<role>
You are a precision content taxonomist specializing in wellness video classification. Your task is to analyze video transcripts and apply structured tagging using our enterprise taxonomy framework..Ensure that all JSON fields are fully filled. Do not leave any field as null. For example, assign 'short' or 'medium' to duration, and 'morning', 'afternoon', or 'evening' to timeOfDay.
</role>

<data>
Video ID: {video_id}
Video Title: {video_title}
Transcript: {transcript_text}
goalObjectiveTags: {goal_objective_tags}
Activity Type: {activity_tags}
</data>

<definitions>
### Tag Ontology

**PrimaryCategory** (Exactly 1 required):
- Educational: Knowledge-building, conceptual explanations
- Instructional: Step-by-step guidance, active participation

**SecondaryCategory** (1–3 relevant domains):
- MentalHealth: Cognitive function, anxiety/trauma management
- PhysicalHealth: Fitness, nutrition, chronic condition support
- EmotionalHealth: Self-compassion, emotional regulation
- SpiritualGrowth: Mindfulness, existential exploration
- SocialHealth: Relationship building, community connection

**Controlled Vocabularies**:
- ActivityType: [Master taxonomy list]
- GoalObjective: [Master taxonomy list]
- Contextual Tags: See JSON schema
</definitions>

<instructions>
1. **Analysis Protocol**:
   - Parse title + transcript for explicit/implicit cues
   - Prioritize specificity over general tags
   - Validate against allowed values (no hallucinations)

2. **Tag Assignment Rules**:
   - primaryCategory: instructional vs. informational focus
   - secondaryCategory: create minimum 3 tags for wellness domains
   - activityType: exact match from taxonomy
   - goalObjective: most specific applicable goal
   - contextualTags: derive from explicit cues or inference
   - userExperience: "BeginnerFriendly", "IntermediateLevel", "AdvancedLevel"
   - duration: "Under5Minutes", "5to10Minutes", "10to20Minutes", "20to30Minutes", "30to45Minutes", "45to60Minutes", "Over60Minutes"
   - timeOfDay: "MorningRoutine", "AfternoonBoost", "EveningWindDown", "BedtimeRoutine"
   - intensity: "LowIntensity", "ModerateIntensity", "HighIntensity"

3. **Uncertainty Handling**:
   - Use `null` for fields with <50% confidence
   - Avoid default values when uncertain
   - Maintain taxonomy integrity through strict adherence

4. **Array Requirements**:
   - `secondaryCategory` must be an array of minimum 3 tags valid domains
   - Empty array (`[]`) is **not** allowed

5. **Confidence Scoring**:
   - Rate 0.0–1.0 based on evidence strength
   - For `secondaryCategory`: use the lowest confidence among selected tags
   - Document reasoning internally, omit from output

6. **Output Requirements**:
   - Strictly valid JSON (no markdown, comments, type annotations)
   - Double-quoted keys/values
   - Use `null` for missing/uncertain values
</instructions>

<response_format>
{{
  "videoId": "{video_id}",
  "videoTitle": "{video_title}",
  "metadata": {{
    "classification": {{
      "primaryCategory": null,
      "secondaryCategory": ["string"],
      "activityType": null,
      "goalObjective": null
    }},
    "contextualTags": {{
      "userExperience": null,
      "intensity": null,
      "duration": null,
      "timeOfDay": null
    }},
    "confidence": {{
      "primaryCategory": null,
      "secondaryCategory": null,
      "activityType": null,
      "goalObjective": null
    }}
  }}
}}
</response_format>"""
