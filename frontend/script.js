// ============================================================
// DARUKAA.EARTH - BIODIVERSITY INTELLIGENCE FRONTEND
// ============================================================

"use strict";


// ============================================================
// API BASE URL
// ============================================================

const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : window.location.origin;


// ============================================================
// SESSION ID
// ============================================================

let sessionId =
    localStorage.getItem("darukaa_session_id");

if (!sessionId) {

    sessionId =
        "session_" +
        Date.now() +
        "_" +
        Math.random()
            .toString(36)
            .substring(2, 10);

    localStorage.setItem(
        "darukaa_session_id",
        sessionId
    );
}


// ============================================================
// DOM HELPER
// ============================================================

function getElement(id) {
    return document.getElementById(id);
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// SAFE VALUE
// ============================================================

function safeValue(
    value,
    fallback = "N/A"
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return fallback;
    }

    return value;
}


// ============================================================
// INPUT HELPERS
// ============================================================

function getInputValue(id) {

    const element =
        getElement(id);

    if (!element) {
        return null;
    }

    const value =
        element.value.trim();

    return value === ""
        ? null
        : value;
}


function getNumberValue(id) {

    const value =
        getInputValue(id);

    if (value === null) {
        return null;
    }

    const number =
        Number(value);

    return Number.isFinite(number)
        ? number
        : null;
}


// ============================================================
// BUILD ENVIRONMENT PROFILE
// ============================================================

function buildEnvironment() {

    return {

        soil: {

            ph:
                getNumberValue("ph"),

            organic_carbon_percent:
                getNumberValue(
                    "organicCarbon"
                ),

            moisture_percent:
                getNumberValue(
                    "moisture"
                )
        },

        climate: {

            rainfall_mm_year:
                getNumberValue(
                    "rainfall"
                ),

            temperature_celsius:
                getNumberValue(
                    "temperature"
                )
        },

        land: {

            land_use:
                getInputValue(
                    "landUse"
                ),

            crop_type:
                getInputValue(
                    "cropType"
                )
        },

        biodiversity: {

            species_richness:
                getInputValue(
                    "speciesRichness"
                ),

            habitat_diversity:
                getInputValue(
                    "habitatDiversity"
                )
        },

        human_impact: {

            pollution_level:
                getInputValue(
                    "pollutionLevel"
                ),

            deforestation_level:
                getInputValue(
                    "deforestationLevel"
                ),

            habitat_fragmentation:
                getInputValue(
                    "habitatFragmentation"
                )
        },

        location: {

            region:
                getInputValue(
                    "region"
                ),

            latitude:
                getNumberValue(
                    "latitude"
                ),

            longitude:
                getNumberValue(
                    "longitude"
                )
        }
    };
}


// ============================================================
// API REQUEST
// ============================================================

async function apiRequest(
    endpoint,
    method = "GET",
    body = null
) {

    const options = {

        method: method,

        headers: {
            "Content-Type":
                "application/json"
        }
    };


    if (body !== null) {

        options.body =
            JSON.stringify(body);
    }


    const response =
        await fetch(
            API_BASE_URL + endpoint,
            options
        );


    let data;

    try {

        data =
            await response.json();

    } catch (error) {

        throw new Error(
            "Server returned an invalid response."
        );
    }


    if (!response.ok) {

        let message =
            data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}.`;


        if (
            typeof message === "object"
        ) {

            message =
                message.message ||
                message.errors?.join(", ") ||
                JSON.stringify(message);
        }


        throw new Error(
            message
        );
    }


    return data;
}


// ============================================================
// BUTTON LOADING
// ============================================================

function setLoading(
    button,
    loading,
    loadingText = "Analyzing..."
) {

    if (!button) {
        return;
    }


    if (loading) {

        button.dataset.originalText =
            button.textContent;

        button.textContent =
            loadingText;

        button.disabled =
            true;

    } else {

        button.textContent =
            button.dataset.originalText ||
            "🔍 Analyze Environment";

        button.disabled =
            false;
    }
}


// ============================================================
// FORMAT OBJECT VALUE
// ============================================================

function formatObjectValue(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    if (
        typeof value === "string" ||
        typeof value === "number" ||
        typeof value === "boolean"
    ) {

        return escapeHTML(value);
    }


    if (Array.isArray(value)) {

        return value
            .map(item =>
                formatObjectValue(item)
            )
            .join(", ");
    }


    if (
        typeof value === "object"
    ) {

        return Object.entries(value)
            .map(
                ([key, val]) => `
                    <div>
                        <strong>
                            ${escapeHTML(key)}:
                        </strong>
                        ${formatObjectValue(val)}
                    </div>
                `
            )
            .join("");
    }


    return escapeHTML(
        String(value)
    );
}


// ============================================================
// RENDER FINDINGS
// ============================================================

function renderFindings(findings) {

    if (
        !Array.isArray(findings) ||
        findings.length === 0
    ) {

        return `
            <p>
                No major environmental findings
                were identified.
            </p>
        `;
    }


    return findings
        .map(
            (finding, index) => {

                if (
                    typeof finding === "string"
                ) {

                    return `
                        <div class="finding-item">

                            <h4>
                                Finding ${index + 1}
                            </h4>

                            <p>
                                ${escapeHTML(
                                    finding
                                )}
                            </p>

                        </div>
                    `;
                }


                if (
                    finding &&
                    typeof finding === "object"
                ) {

                    const factor =
                        finding.factor ||
                        finding.issue ||
                        finding.finding ||
                        finding.problem ||
                        finding.name ||
                        "Environmental issue";


                    const severity =
                        finding.severity ||
                        finding.level ||
                        "";


                    const explanation =
                        finding.explanation ||
                        finding.reasoning ||
                        finding.impact ||
                        finding.description ||
                        "";


                    return `
                        <div class="finding-item">

                            <h4>
                                ${escapeHTML(
                                    factor
                                )}
                            </h4>

                            ${
                                severity
                                    ? `
                                        <p>
                                            <strong>
                                                Severity:
                                            </strong>

                                            ${escapeHTML(
                                                severity
                                            )}
                                        </p>
                                    `
                                    : ""
                            }

                            ${
                                explanation
                                    ? `
                                        <p>
                                            ${escapeHTML(
                                                explanation
                                            )}
                                        </p>
                                    `
                                    : ""
                            }

                        </div>
                    `;
                }


                return `
                    <div class="finding-item">

                        ${formatObjectValue(
                            finding
                        )}

                    </div>
                `;
            }
        )
        .join("");
}


// ============================================================
// RENDER MULTI-METRIC INTERACTIONS
// ============================================================

function renderInteractions(
    interactions
) {

    if (
        !Array.isArray(interactions) ||
        interactions.length === 0
    ) {

        return `
            <p>
                No multi-metric interactions
                were identified.
            </p>
        `;
    }


    return interactions
        .map(
            (interaction, index) => {

                if (
                    typeof interaction === "string"
                ) {

                    return `
                        <div class="interaction-item">

                            <h4>
                                Interaction ${index + 1}
                            </h4>

                            <p>
                                ${escapeHTML(
                                    interaction
                                )}
                            </p>

                        </div>
                    `;
                }


                if (
                    interaction &&
                    typeof interaction === "object"
                ) {

                    const title =
                        interaction.interaction ||
                        interaction.title ||
                        interaction.name ||
                        "Environmental interaction";


                    const reasoning =
                        interaction.reasoning ||
                        interaction.explanation ||
                        interaction.description ||
                        "";


                    return `
                        <div class="interaction-item">

                            <h4>
                                ${escapeHTML(
                                    title
                                )}
                            </h4>

                            ${
                                reasoning
                                    ? `
                                        <p>
                                            ${escapeHTML(
                                                reasoning
                                            )}
                                        </p>
                                    `
                                    : ""
                            }

                        </div>
                    `;
                }


                return `
                    <div class="interaction-item">

                        ${formatObjectValue(
                            interaction
                        )}

                    </div>
                `;
            }
        )
        .join("");
}


// ============================================================
// RENDER RECOMMENDATIONS
// ============================================================

function renderRecommendations(
    recommendations
) {

    if (
        !Array.isArray(recommendations) ||
        recommendations.length === 0
    ) {

        return `
            <p>
                No specific recommendations
                were generated.
            </p>
        `;
    }


    return recommendations
        .map(
            (recommendation, index) => {

                if (
                    typeof recommendation === "string"
                ) {

                    return `
                        <div class="recommendation-card">

                            <h4>
                                Recommendation ${index + 1}
                            </h4>

                            <p>
                                ${escapeHTML(
                                    recommendation
                                )}
                            </p>

                        </div>
                    `;
                }


                const action =
                    recommendation.action ||
                    recommendation.recommendation ||
                    recommendation.title ||
                    recommendation.intervention ||
                    `Recommendation ${index + 1}`;


                const why =
                    recommendation.why_it_works ||
                    recommendation.reasoning ||
                    recommendation.explanation ||
                    recommendation.why ||
                    "";


                const metrics =
                    Array.isArray(
                        recommendation.impacted_metrics
                    )
                        ? recommendation.impacted_metrics
                        : [];


                const timeHorizon =
                    recommendation.time_horizon ||
                    recommendation.timeline ||
                    recommendation.timeframe ||
                    "";


                const confidence =
                    recommendation.confidence ||
                    "";


                return `
                    <div class="recommendation-card">

                        <h4>
                            ${escapeHTML(
                                action
                            )}
                        </h4>

                        ${
                            why
                                ? `
                                    <p>
                                        <strong>
                                            Why it works:
                                        </strong>
                                    </p>

                                    <p>
                                        ${escapeHTML(
                                            why
                                        )}
                                    </p>
                                `
                                : ""
                        }

                        ${
                            metrics.length > 0
                                ? `
                                    <p>
                                        <strong>
                                            Impacted metrics:
                                        </strong>
                                    </p>

                                    <div class="metric-list">

                                        ${metrics
                                            .map(
                                                metric => `
                                                    <span class="metric-tag">
                                                        ${escapeHTML(
                                                            metric
                                                        )}
                                                    </span>
                                                `
                                            )
                                            .join("")}

                                    </div>
                                `
                                : ""
                        }

                        ${
                            timeHorizon
                                ? `
                                    <p>
                                        <strong>
                                            Time horizon:
                                        </strong>

                                        ${escapeHTML(
                                            timeHorizon
                                        )}
                                    </p>
                                `
                                : ""
                        }

                        ${
                            confidence
                                ? `
                                    <p>
                                        <strong>
                                            Confidence:
                                        </strong>

                                        ${escapeHTML(
                                            confidence
                                        )}
                                    </p>
                                `
                                : ""
                        }

                    </div>
                `;
            }
        )
        .join("");
}


// ============================================================
// RENDER SCIENTIFIC EVIDENCE
// ============================================================

function renderScientificEvidence(
    evidence
) {

    if (
        !Array.isArray(evidence) ||
        evidence.length === 0
    ) {

        return `
            <p>
                No scientific evidence was retrieved.
            </p>
        `;
    }


    return evidence
        .map(
            (item, index) => {

                if (
                    typeof item === "string"
                ) {

                    return `
                        <div class="evidence-card">

                            <h4>
                                Evidence ${index + 1}
                            </h4>

                            <p>
                                ${escapeHTML(
                                    item
                                )}
                            </p>

                        </div>
                    `;
                }


                const source =
                    item.source ||
                    item.title ||
                    "Scientific source";


                const page =
                    item.page ??
                    "Unknown";


                const text =
                    item.evidence ||
                    item.text ||
                    item.content ||
                    item.description ||
                    "";


                return `
                    <div class="evidence-card">

                        <h4>
                            ${escapeHTML(
                                source
                            )}
                        </h4>

                        <p>
                            <strong>
                                Page:
                            </strong>

                            ${escapeHTML(
                                page
                            )}
                        </p>

                        ${
                            text
                                ? `
                                    <p>
                                        ${escapeHTML(
                                            text
                                        )}
                                    </p>
                                `
                                : ""
                        }

                    </div>
                `;
            }
        )
        .join("");
}


// ============================================================
// RENDER LOCATION BIODIVERSITY / GBIF
// ============================================================

function renderLocationBiodiversity(
    gbif
) {

    if (
        !gbif ||
        typeof gbif !== "object"
    ) {

        return `
            <p>
                No location biodiversity
                information available.
            </p>
        `;
    }


    if (
        gbif.available === false
    ) {

        return `
            <div>

                <p>
                    GBIF biodiversity data
                    is currently unavailable.
                </p>

                ${
                    gbif.error
                        ? `
                            <small>
                                ${escapeHTML(
                                    gbif.error
                                )}
                            </small>
                        `
                        : ""
                }

            </div>
        `;
    }


    const recordCount =
        gbif.record_count ??
        gbif.count ??
        0;


    const returnedRecords =
        gbif.returned_records ??
        0;


    const observedTaxaCount =
        gbif.observed_taxa_count ??
        gbif.taxa_count ??
        0;


    let observedTaxa =
        Array.isArray(
            gbif.observed_taxa
        )
            ? gbif.observed_taxa
            : [];


    observedTaxa =
        observedTaxa.map(
            taxon => {

                if (
                    taxon &&
                    typeof taxon === "object"
                ) {

                    return (
                        taxon.scientificName ||
                        taxon.name ||
                        taxon.taxon ||
                        JSON.stringify(taxon)
                    );
                }

                return taxon;
            }
        );


    const latitude =
        gbif.latitude ??
        null;


    const longitude =
        gbif.longitude ??
        null;


    const radius =
        gbif.radius_km ??
        gbif.radius ??
        null;


    return `

        <div class="gbif-summary">

            <div class="gbif-stat">

                <strong>
                    ${escapeHTML(
                        recordCount
                    )}
                </strong>

                <span>
                    GBIF records
                </span>

            </div>


            <div class="gbif-stat">

                <strong>
                    ${escapeHTML(
                        returnedRecords
                    )}
                </strong>

                <span>
                    Records returned
                </span>

            </div>


            <div class="gbif-stat">

                <strong>
                    ${escapeHTML(
                        observedTaxaCount
                    )}
                </strong>

                <span>
                    Observed taxa
                </span>

            </div>

        </div>


        ${
            latitude !== null &&
            longitude !== null
                ? `
                    <p>

                        <strong>
                            Search location:
                        </strong>

                        ${escapeHTML(
                            latitude
                        )},
                        ${escapeHTML(
                            longitude
                        )}

                        ${
                            radius !== null
                                ? `
                                    (${escapeHTML(
                                        radius
                                    )} km radius)
                                `
                                : ""
                        }

                    </p>
                `
                : ""
        }


        ${
            observedTaxa.length > 0
                ? `

                    <h4>
                        Observed taxa
                    </h4>

                    <ul>

                        ${observedTaxa
                            .slice(0, 20)
                            .map(
                                taxon => `
                                    <li>
                                        ${escapeHTML(
                                            taxon
                                        )}
                                    </li>
                                `
                            )
                            .join("")}

                    </ul>

                    ${
                        observedTaxa.length > 20
                            ? `
                                <small>
                                    Showing the first
                                    20 observed taxa.
                                </small>
                            `
                            : ""
                    }

                `
                : `
                    <p>
                        No observed taxa were
                        returned by GBIF.
                    </p>
                `
        }


        <p>

            <strong>
                Note:
            </strong>

            GBIF occurrence records provide
            geographic biodiversity context.
            They are not a complete measurement
            of true species richness, and missing
            observations do not prove species absence.

        </p>

    `;
}


// ============================================================
// RENDER LOCATION
// ============================================================

function renderLocation(
    environment
) {

    const location =
        environment?.location || {};


    const region =
        location.region;


    const latitude =
        location.latitude;


    const longitude =
        location.longitude;


    if (
        !region &&
        latitude === null &&
        latitude === undefined &&
        longitude === null &&
        longitude === undefined
    ) {

        return `
            <p>
                No location information provided.
            </p>
        `;
    }


    return `

        <div class="location-info">

            ${
                region
                    ? `
                        <p>

                            <strong>
                                Region:
                            </strong>

                            ${escapeHTML(
                                region
                            )}

                        </p>
                    `
                    : ""
            }


            ${
                latitude !== null &&
                latitude !== undefined
                    ? `
                        <p>

                            <strong>
                                Latitude:
                            </strong>

                            ${escapeHTML(
                                latitude
                            )}

                        </p>
                    `
                    : ""
            }


            ${
                longitude !== null &&
                longitude !== undefined
                    ? `
                        <p>

                            <strong>
                                Longitude:
                            </strong>

                            ${escapeHTML(
                                longitude
                            )}

                        </p>
                    `
                    : ""
            }

        </div>

    `;
}


// ============================================================
// RENDER DATA LIMITATIONS
// ============================================================

function renderDataLimitations(
    limitations
) {

    if (
        !Array.isArray(limitations) ||
        limitations.length === 0
    ) {

        return `
            <p>
                No additional data limitations reported.
            </p>
        `;
    }


    return `

        <ul>

            ${limitations
                .map(
                    item => {

                        if (
                            item &&
                            typeof item === "object"
                        ) {

                            return `
                                <li>
                                    ${escapeHTML(
                                        item.description ||
                                        item.message ||
                                        item.reason ||
                                        JSON.stringify(item)
                                    )}
                                </li>
                            `;
                        }


                        return `
                            <li>
                                ${escapeHTML(
                                    item
                                )}
                            </li>
                        `;
                    }
                )
                .join("")}

        </ul>

    `;
}


// ============================================================
// RENDER ASSESSMENT
// ============================================================

function renderAssessment(
    response,
    analysis
) {

    const assessment =
        response?.assessment ||
        analysis?.overall_assessment ||
        analysis?.assessment ||
        analysis?.overall;


    if (!assessment) {

        return `
            <p>
                No overall assessment was returned.
            </p>
        `;
    }


    return `
        <p>
            ${escapeHTML(
                assessment
            )}
        </p>
    `;
}


// ============================================================
// DISPLAY COMPLETE ANALYSIS
// ============================================================

function displayAnalysis(
    data
) {

    console.log(
        "Darukaa analysis response:",
        data
    );


    const resultsSection =
        getElement(
            "analysisResults"
        );


    const resultsContent =
        getElement(
            "resultsContent"
        );


    if (!resultsSection) {

        console.error(
            "analysisResults element not found."
        );

        return;
    }


    if (!resultsContent) {

        console.error(
            "resultsContent element not found."
        );

        return;
    }


    const analysis =
        data.analysis || {};


    const response =
        data.response || {};


    const findings =
        Array.isArray(
            analysis.findings
        )
            ? analysis.findings
            : [];


    const interactions =
        Array.isArray(
            response.key_interactions
        )
            ? response.key_interactions
            : (
                Array.isArray(
                    analysis.interactions
                )
                    ? analysis.interactions
                    : []
            );


    const recommendations =
        Array.isArray(
            response.recommendations
        )
            ? response.recommendations
            : (
                Array.isArray(
                    analysis.recommendations
                )
                    ? analysis.recommendations
                    : []
            );


    const evidence =
        Array.isArray(
            response.scientific_evidence
        )
            ? response.scientific_evidence
            : (
                Array.isArray(
                    data.scientific_evidence
                )
                    ? data.scientific_evidence
                    : []
            );


    const limitations =
        Array.isArray(
            response.data_limitations
        )
            ? response.data_limitations
            : (
                Array.isArray(
                    data.data_quality?.warnings
                )
                    ? data.data_quality.warnings
                    : []
            );


    resultsContent.innerHTML = `

        <!-- OVERALL ASSESSMENT -->

        <div class="analysis-block">

            <h3>
                🌍 Overall Assessment
            </h3>

            <div class="assessment-box">

                ${renderAssessment(
                    response,
                    analysis
                )}

            </div>

        </div>


        <!-- ENVIRONMENTAL FINDINGS -->

        <div class="analysis-block">

            <h3>
                🔎 Key Environmental Findings
            </h3>

            <div class="findings-box">

                ${renderFindings(
                    findings
                )}

            </div>

        </div>


        <!-- MULTI-METRIC INTERACTIONS -->

        <div class="analysis-block">

            <h3>
                🔗 Multi-Metric Interactions
            </h3>

            <div class="interactions-box">

                ${renderInteractions(
                    interactions
                )}

            </div>

        </div>


        <!-- RECOMMENDATIONS -->

        <div class="analysis-block">

            <h3>
                🌱 Recommendations
            </h3>

            <div class="recommendations-box">

                ${renderRecommendations(
                    recommendations
                )}

            </div>

        </div>


        <!-- SCIENTIFIC EVIDENCE -->

        <div class="analysis-block">

            <h3>
                🔬 Scientific Evidence
            </h3>

            <div class="evidence-box">

                ${renderScientificEvidence(
                    evidence
                )}

            </div>

        </div>


        <!-- LOCATION -->

        <div class="analysis-block">

            <h3>
                📍 Location
            </h3>

            ${renderLocation(
                data.environment
            )}

        </div>


        <!-- LOCATION BIODIVERSITY -->

        <div class="analysis-block">

            <h3>
                📍 Location Biodiversity
            </h3>

            ${renderLocationBiodiversity(
                data.location_biodiversity
            )}

        </div>


        <!-- DATA LIMITATIONS -->

        <div class="analysis-block">

            <h3>
                ⚠️ Data Limitations
            </h3>

            ${renderDataLimitations(
                limitations
            )}

        </div>


        <!-- DATA QUALITY -->

        ${
            data.data_quality
                ? `
                    <div class="analysis-block">

                        <h3>
                            📋 Data Quality
                        </h3>

                        <p>

                            <strong>
                                Data completeness:
                            </strong>

                            ${escapeHTML(
                                safeValue(
                                    data.data_quality
                                        .completeness_percent,
                                    0
                                )
                            )}%

                        </p>

                        ${
                            Array.isArray(
                                data.data_quality.warnings
                            ) &&
                            data.data_quality.warnings.length > 0
                                ? `
                                    <ul>

                                        ${data.data_quality.warnings
                                            .map(
                                                warning => `
                                                    <li>
                                                        ${escapeHTML(
                                                            warning
                                                        )}
                                                    </li>
                                                `
                                            )
                                            .join("")}

                                    </ul>
                                `
                                : ""
                        }

                    </div>
                `
                : ""
        }

    `;


    resultsSection.style.display =
        "block";


    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });


    console.log(
        "Analysis displayed successfully."
    );
}


// ============================================================
// ANALYZE ENVIRONMENT
// ============================================================

async function analyzeEnvironment() {

    const button =
        getElement(
            "analyzeBtn"
        );


    try {

        setLoading(
            button,
            true,
            "Analyzing..."
        );


        const environment =
            buildEnvironment();


        const question =
            getInputValue(
                "question"
            ) ||
            "Analyze this environment and provide biodiversity recommendations.";


        console.log(
            "Sending environment:",
            environment
        );


        const data =
            await apiRequest(
                "/analyze",
                "POST",
                {
                    question:
                        question,

                    environment:
                        environment
                }
            );


        displayAnalysis(
            data
        );


    } catch (error) {

        console.error(
            "Biodiversity analysis error:",
            error
        );


        alert(
            "Biodiversity analysis failed:\n\n" +
            error.message
        );


    } finally {

        setLoading(
            button,
            false
        );
    }
}


// ============================================================
// CHAT MESSAGE
// ============================================================

function addChatMessage(
    role,
    message
) {

    const chatContainer =
        getElement(
            "chatMessages"
        );


    if (!chatContainer) {
        return;
    }


    const messageDiv =
        document.createElement(
            "div"
        );


    messageDiv.className =
        `message ${role}`;


    let text;


    if (
        message &&
        typeof message === "object"
    ) {

        text =
            message.assessment ||
            message.message ||
            JSON.stringify(
                message
            );

    } else {

        text =
            String(message);
    }


    messageDiv.innerHTML = `

        <strong>
            ${
                role === "user"
                    ? "You"
                    : "Darukaa.Earth"
            }
        </strong>

        <p>
            ${escapeHTML(
                text
            )}
        </p>

    `;


    chatContainer.appendChild(
        messageDiv
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// ============================================================
// SEND CHAT MESSAGE
// ============================================================

async function sendChatMessage() {

    const input =
        getElement(
            "question"
        );


    const button =
        getElement(
            "sendButton"
        );


    if (!input) {
        return;
    }


    const question =
        input.value.trim();


    if (!question) {

        return;
    }


    try {

        addChatMessage(
            "user",
            question
        );


        input.value =
            "";


        setLoading(
            button,
            true,
            "Thinking..."
        );


        const environment =
            buildEnvironment();


        const data =
            await apiRequest(
                "/chat",
                "POST",
                {
                    session_id:
                        sessionId,

                    question:
                        question,

                    environment:
                        environment
                }
            );


        const response =
            data.response || {};


        const assistantMessage =
            response.assessment ||
            response.message ||
            "Analysis completed successfully.";


        addChatMessage(
            "assistant",
            assistantMessage
        );


        displayAnalysis(
            data
        );


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        addChatMessage(
            "assistant",
            "Sorry, I could not process your request."
        );


        alert(
            "Chat failed:\n\n" +
            error.message
        );


    } finally {

        setLoading(
            button,
            false
        );
    }
}


// ============================================================
// CLEAR FORM
// ============================================================

function clearForm() {

    const fieldIds = [

        "ph",
        "organicCarbon",
        "moisture",

        "rainfall",
        "temperature",

        "landUse",
        "cropType",

        "speciesRichness",
        "habitatDiversity",

        "pollutionLevel",
        "deforestationLevel",
        "habitatFragmentation",

        "region",
        "latitude",
        "longitude",

        "question"
    ];


    fieldIds.forEach(
        id => {

            const element =
                getElement(id);


            if (element) {

                element.value =
                    "";
            }
        }
    );


    const resultsSection =
        getElement(
            "analysisResults"
        );


    const resultsContent =
        getElement(
            "resultsContent"
        );


    if (resultsContent) {

        resultsContent.innerHTML =
            "";
    }


    if (resultsSection) {

        resultsSection.style.display =
            "none";
    }
}


// ============================================================
// CLEAR CHAT
// ============================================================

function clearChat() {

    const chatContainer =
        getElement(
            "chatMessages"
        );


    if (chatContainer) {

        chatContainer.innerHTML = `

            <div class="message assistant">

                <strong>
                    Darukaa.Earth
                </strong>

                <p>
                    Hello! Enter your environmental
                    information above and ask me
                    a question about your ecosystem.
                </p>

            </div>

        `;
    }


    sessionId =
        "session_" +
        Date.now() +
        "_" +
        Math.random()
            .toString(36)
            .substring(2, 10);


    localStorage.setItem(
        "darukaa_session_id",
        sessionId
    );
}


// ============================================================
// SUGGESTION BUTTON
// ============================================================

function useSuggestion(
    text
) {

    const input =
        getElement(
            "question"
        );


    if (!input) {
        return;
    }


    input.value =
        text;

    input.focus();
}


// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "Darukaa.Earth frontend initialized."
        );


        // ----------------------------------------------------
        // ANALYZE BUTTON
        // ----------------------------------------------------

        const analyzeButton =
            getElement(
                "analyzeBtn"
            );


        if (analyzeButton) {

            analyzeButton.addEventListener(
                "click",
                analyzeEnvironment
            );
        }


        // ----------------------------------------------------
        // SEND CHAT BUTTON
        // ----------------------------------------------------

        const sendButton =
            getElement(
                "sendButton"
            );


        if (sendButton) {

            sendButton.addEventListener(
                "click",
                sendChatMessage
            );
        }


        // ----------------------------------------------------
        // ENTER KEY FOR CHAT
        // ----------------------------------------------------

        const questionInput =
            getElement(
                "question"
            );


        if (questionInput) {

            questionInput.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key === "Enter" &&
                        !event.shiftKey
                    ) {

                        event.preventDefault();

                        sendChatMessage();
                    }
                }
            );
        }


        // ----------------------------------------------------
        // CLEAR BUTTON
        // ----------------------------------------------------

        const clearButton =
            getElement(
                "clearBtn"
            );


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                clearForm
            );
        }


        // ----------------------------------------------------
        // OPTIONAL CLEAR CHAT BUTTON
        // ----------------------------------------------------

        const clearChatButton =
            getElement(
                "clearChat"
            );


        if (clearChatButton) {

            clearChatButton.addEventListener(
                "click",
                clearChat
            );
        }


        // ----------------------------------------------------
        // SUGGESTION BUTTONS
        // ----------------------------------------------------

        const suggestionButtons =
            document.querySelectorAll(
                "[data-suggestion]"
            );


        suggestionButtons.forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        useSuggestion(
                            button.dataset.suggestion
                        );
                    }
                );
            }
        );

    }
);