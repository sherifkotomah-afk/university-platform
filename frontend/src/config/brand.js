/**
 * WHITE-LABEL CONFIG
 * ===================
 * This is the ONE file to edit when repackaging this platform for a
 * different university/investor pitch. Nothing else in the codebase
 * should need to change for a basic rebrand (name, colors, logo).
 *
 * Deeper settings (grading system, levy list, academic year) live in
 * the `institution_settings` table in the database, editable from the
 * Admin dashboard — those can differ per deployment without a redeploy.
 */
export const BRAND = {
  institutionName: "Sample University",
  shortCode: "SU",
  logoUrl: "/logo.svg",
  primaryColor: "#1a1a2e",
  secondaryColor: "#f5b400",
  contactEmail: "info@sampleuniversity.edu.gh",
  contactPhone: "+233 000 000 000",
  address: "Accra, Ghana",
  tagline: "Excellence in Education",
}
