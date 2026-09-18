// ============================================================
// DARUKAA.EARTH - BIODIVERSITY INTELLIGENCE FRONTEND
// ============================================================

// ------------------------------------------------------------
// API BASE URL
// ------------------------------------------------------------

const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : window.location.origin;


// ------------------------------------------------------------
// SESSION ID
// ------------------------------------------------------------

let sessionId = localStorage.getItem("darukaa_session_id");

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


// ------------------------------------------------------------
// DOM HELPERS
// ------------------------------------------------------------

function getElement(...ids) {

    for (const id of ids) {

        const element = document.getElementById(id);

        if (element) {
            return element;
        }
    }

    return null;
}


function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function safeValue(value, fallback = "N/A") {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return fallback;
    }

    return value;
}


// ------------------------------------------------------------
// GET INPUT VALUE
// ------------------------------------------------------------

function getInputValue(id) {

    const element = document.getElementById(id);

    if (!element) {
        return null;
    }

    const value = element.value.trim();

    return value === "" ? null : value;
}


function getNumberValue(id) {

    const value = getInputValue(id);

    if (value === null) {
        return null;
    }

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : null;
}


// ------------------------------------------------------------
// BUILD ENVIRONMENT PROFILE
// ------------------------------------------------------------

function buildEnvironment() {

    return {

        soil: {

            ph: getNumberValue("ph"),

            organic_carbon_percent:
                getNumberValue("organicCarbon"),

            moisture_percent:
                getNumberValue("moisture")
        },


        climate: {

            rainfall_mm_year:
                getNumberValue("rainfall"),

            temperature_celsius:
                getNumberValue("temperature")
        },


        land: {

            land_use:
                getInputValue("landUse"),

            crop_type:
                getInputValue("cropType")
        },


        biodiversity: {

            species_richness:
                getInputValue("speciesRichness"),

            habitat_diversity:
                getInputValue("habitatDiversity")
        },


        human_impact: {

            pollution_level:
                getInputValue("pollutionLevel"),

            deforestation_level:
                getInputValue("deforestationLevel"),

            habitat_fragmentation:
                getInputValue("habitatFragmentation")
        },


        location: {

            region:
                getInputValue("region"),

            latitude:
                getNumberValue("latitude"),

            longitude:
                getNumberValue("longitude")
        }
    };
}


// ------------------------------------------------------------
// API REQUEST
// ------------------------------------------------------------

async function apiRequest(
    endpoint,
    method = "GET",
    body = null
) {

    const options = {

        method,

        headers: {
            "Content-Type": "application/json"
        }
    };


    if (body !== null) {

        options.body = JSON.stringify(body);
    }


    const response = await fetch(
        API_BASE_URL + endpoint,
        options
    );


    let data = null;

    try {

        data = await response.json();

    } catch (error) {

        throw new Error(
            `Server returned an invalid response (${response.status}).`
        );
    }


    if (!response.ok) {

        let message =
            data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}.`;


        // FastAPI HTTPException detail can be an object

        if (typeof message === "object") {

            message =
                message.message ||
                message.errors?.join(", ") ||
                JSON.stringify(message);
        }


        throw new Error(message);
    }


    return data;
}


// ------------------------------------------------------------
// SHOW STATUS
// ------------------------------------------------------------

function showStatus(message, type = "info") {

    let statusElement =
        getElement(
            "statusMessage",
            "status",
            "apiStatus"
        );


    if (!statusElement) {
        return;
    }


    statusElement.textContent = message;

    statusElement.className =
        `status-message ${type}`;
}


// ------------------------------------------------------------
// SHOW LOADING
// ------------------------------------------------------------

function setLoading(
    button,
    loading,
    loadingText = "Processing..."
) {

    if (!button) {
        return;
    }


    if (loading) {

        button.dataset.originalText =
            button.textContent;

        button.textContent =
            loadingText;

        button.disabled = true;

    } else {

        button.textContent =
            button.dataset.originalText ||
            button.textContent;

        button.disabled = false;
    }
}


// ------------------------------------------------------------
// FINDINGS
// ------------------------------------------------------------

function renderFindings(findings) {

    if (
        !Array.isArray(findings) ||
        findings.length === 0
    ) {

        return `
            <p class="empty-message">
                No major environmental findings identified.
            </p>
        `;
    }


    return findings
        .map((finding) => {

            // --------------------------------------------
            // STRING FINDING
            // --------------------------------------------

            if (typeof finding === "string") {

                return `
                    <div class="finding-item">
                        <div class="finding-text">
                            ${escapeHTML(finding)}
                        </div>
                    </div>
                `;
            }


            // --------------------------------------------
            // OBJECT FINDING
            // --------------------------------------------

            if (
                finding &&
                typeof finding === "object"
            ) {

                const issue =
                    finding.issue ||
                    finding.finding ||
                    finding.problem ||
                    finding.description ||
                    finding.name ||
                    "Environmental issue identified";


                const severity =
                    finding.severity ||
                    finding.level ||
                    finding.priority ||
                    "";


                const variables =
                    Array.isArray(finding.variables)
                        ? finding.variables
                        : [];


                const reasoning =
                    finding.reasoning ||
                    finding.explanation ||
                    finding.impact ||
                    "";


                return `
                    <div class="finding-item">

                        <div class="finding-title">
                            ${escapeHTML(issue)}
                        </div>

                        ${
                            severity
                                ? `
                                    <div class="finding-severity">
                                        Severity:
                                        ${escapeHTML(severity)}
                                    </div>
                                  `
                                : ""
                        }

                        ${
                            variables.length > 0
                                ? `
                                    <div class="finding-variables">
                                        Variables:
                                        ${escapeHTML(
                                            variables.join(", ")
                                        )}
                                    </div>
                                  `
                                : ""
                        }

                        ${
                            reasoning
                                ? `
                                    <div class="finding-reasoning">
                                        ${escapeHTML(reasoning)}
                                    </div>
                                  `
                                : ""
                        }

                    </div>
                `;
            }


            // --------------------------------------------
            // UNKNOWN VALUE
            // --------------------------------------------

            return `
                <div class="finding-item">
                    ${escapeHTML(String(finding))}
                </div>
            `;

        })
        .join("");
}


// ------------------------------------------------------------
// MULTI-METRIC INTERACTIONS
// ------------------------------------------------------------

function renderInteractions(interactions) {

    if (
        !Array.isArray(interactions) ||
        interactions.length === 0
    ) {

        return `
            <p class="empty-message">
                No multi-metric interactions identified.
            </p>
        `;
    }


    return interactions
        .map((interaction) => {

            // --------------------------------------------
            // OBJECT
            // --------------------------------------------

            if (
                interaction &&
                typeof interaction === "object"
            ) {

                let variables = [];


                if (
                    Array.isArray(
                        interaction.variables
                    )
                ) {

                    variables =
                        interaction.variables;

                } else if (
                    Array.isArray(
                        interaction.metrics
                    )
                ) {

                    variables =
                        interaction.metrics;

                } else if (
                    Array.isArray(
                        interaction.factors
                    )
                ) {

                    variables =
                        interaction.factors;
                }


                const title =
                    interaction.interaction ||
                    interaction.title ||
                    interaction.name ||
                    (
                        variables.length > 0
                            ? variables.join(" + ")
                            : "Environmental interaction"
                    );


                const reasoning =
                    interaction.reasoning ||
                    interaction.explanation ||
                    interaction.description ||
                    "";


                return `
                    <div class="interaction-item">

                        <h4>
                            ${escapeHTML(title)}
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


            // --------------------------------------------
            // STRING
            // --------------------------------------------

            return `
                <div class="interaction-item">
                    <p>${escapeHTML(interaction)}</p>
                </div>
            `;

        })
        .join("");
}


// ------------------------------------------------------------
// RECOMMENDATIONS
// ------------------------------------------------------------

function renderRecommendations(
    recommendations
) {

    if (
        !Array.isArray(recommendations) ||
        recommendations.length === 0
    ) {

        return `
            <p class="empty-message">
                No specific recommendations were generated.
            </p>
        `;
    }


    return recommendations
        .map((recommendation, index) => {

            // --------------------------------------------
            // STRING
            // --------------------------------------------

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


            // --------------------------------------------
            // OBJECT
            // --------------------------------------------

            const action =
                recommendation.action ||
                recommendation.recommendation ||
                recommendation.title ||
                recommendation.intervention ||
                "Environmental intervention";


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
                        ${escapeHTML(action)}
                    </h4>


                    ${
                        why
                            ? `
                                <div class="recommendation-section">

                                    <strong>
                                        Why it works:
                                    </strong>

                                    <p>
                                        ${escapeHTML(why)}
                                    </p>

                                </div>
                              `
                            : ""
                    }


                    ${
                        metrics.length > 0
                            ? `
                                <div class="recommendation-section">

                                    <strong>
                                        Impacted metrics:
                                    </strong>

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

                                </div>
                              `
                            : ""
                    }


                    ${
                        timeHorizon
                            ? `
                                <div class="recommendation-section">

                                    <strong>
                                        Time horizon:
                                    </strong>

                                    <span>
                                        ${escapeHTML(
                                            timeHorizon
                                        )}
                                    </span>

                                </div>
                              `
                            : ""
                    }


                    ${
                        confidence
                            ? `
                                <div class="recommendation-section">

                                    <strong>
                                        Confidence:
                                    </strong>

                                    <span>
                                        ${escapeHTML(
                                            confidence
                                        )}
                                    </span>

                                </div>
                              `
                            : ""
                    }

                </div>
            `;

        })
        .join("");
}


// ------------------------------------------------------------
// SCIENTIFIC EVIDENCE
// ------------------------------------------------------------

function renderScientificEvidence(
    evidence
) {

    if (
        !Array.isArray(evidence) ||
        evidence.length === 0
    ) {

        return `
            <p class="empty-message">
                No scientific evidence was retrieved.
            </p>
        `;
    }


    return evidence
        .map((item, index) => {

            if (
                typeof item === "string"
            ) {

                return `
                    <div class="evidence-card">

                        <h4>
                            Evidence ${index + 1}
                        </h4>

                        <p>
                            ${escapeHTML(item)}
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
                        ${escapeHTML(source)}
                    </h4>


                    <div class="evidence-page">

                        Page:
                        ${escapeHTML(page)}

                    </div>


                    ${
                        text
                            ? `
                                <p>
                                    ${escapeHTML(text)}
                                </p>
                              `
                            : ""
                    }

                </div>
            `;

        })
        .join("");
}


// ------------------------------------------------------------
// DATA LIMITATIONS
// ------------------------------------------------------------

function renderDataLimitations(
    limitations
) {

    if (
        !Array.isArray(limitations) ||
        limitations.length === 0
    ) {

        return `
            <p class="empty-message">
                No additional data limitations reported.
            </p>
        `;
    }


    return `
        <ul class="limitations-list">

            ${limitations
                .map((item) => {

                    if (
                        typeof item === "object" &&
                        item !== null
                    ) {

                        const text =
                            item.description ||
                            item.message ||
                            item.reason ||
                            JSON.stringify(item);

                        return `
                            <li>
                                ${escapeHTML(text)}
                            </li>
                        `;
                    }


                    return `
                        <li>
                            ${escapeHTML(item)}
                        </li>
                    `;

                })
                .join("")}

        </ul>
    `;
}


// ------------------------------------------------------------
// LOCATION BIODIVERSITY / GBIF
// ------------------------------------------------------------

function renderLocationBiodiversity(
    gbif
) {

    if (
        !gbif ||
        typeof gbif !== "object"
    ) {

        return `
            <p class="empty-message">
                No location biodiversity information available.
            </p>
        `;
    }


    // --------------------------------------------
    // GBIF UNAVAILABLE
    // --------------------------------------------

    if (gbif.available === false) {

        return `
            <div class="gbif-unavailable">

                <p>
                    GBIF biodiversity data is currently unavailable.
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


    // --------------------------------------------
    // DATA
    // --------------------------------------------

    const recordCount =
        gbif.record_count ??
        gbif.count ??
        0;


    const returnedRecords =
        gbif.returned_records ??
        gbif.limit ??
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


    // Some APIs may return objects

    observedTaxa =
        observedTaxa.map((taxon) => {

            if (
                typeof taxon === "object" &&
                taxon !== null
            ) {

                return (
                    taxon.scientificName ||
                    taxon.name ||
                    taxon.taxon ||
                    JSON.stringify(taxon)
                );
            }

            return taxon;
        });


    const latitude =
        gbif.latitude ??
        gbif.center_latitude ??
        null;


    const longitude =
        gbif.longitude ??
        gbif.center_longitude ??
        null;


    const radius =
        gbif.radius_km ??
        gbif.radius ??
        null;


    return `

        <div class="gbif-summary">

            <div class="gbif-stat">

                <strong>
                    ${escapeHTML(recordCount)}
                </strong>

                <span>
                    GBIF records
                </span>

            </div>


            <div class="gbif-stat">

                <strong>
                    ${escapeHTML(returnedRecords)}
                </strong>

                <span>
                    Records returned
                </span>

            </div>


            <div class="gbif-stat">

                <strong>
                    ${escapeHTML(observedTaxaCount)}
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
                    <div class="gbif-location">

                        <strong>
                            Search location:
                        </strong>

                        ${escapeHTML(latitude)},
                        ${escapeHTML(longitude)}

                        ${
                            radius !== null
                                ? `
                                    <span>
                                        (${escapeHTML(radius)} km radius)
                                    </span>
                                  `
                                : ""
                        }

                    </div>
                  `
                : ""
        }


        ${
            observedTaxa.length > 0
                ? `
                    <div class="gbif-species">

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

                    </div>
                  `
                : `
                    <p class="empty-message">
                        No observed taxa were returned by GBIF.
                    </p>
                  `
        }


        <p class="gbif-note">

            GBIF occurrence records provide geographic
            biodiversity context. They are not a complete
            measurement of true species richness, and missing
            observations do not prove species absence.

        </p>

    `;
}


// ------------------------------------------------------------
// LOCATION INFORMATION
// ------------------------------------------------------------

function renderLocation(
    environment
) {

    if (
        !environment ||
        typeof environment !== "object"
    ) {

        return "";
    }


    const location =
        environment.location ||
        {};


    const region =
        location.region;


    const latitude =
        location.latitude;


    const longitude =
        location.longitude;


    if (
        !region &&
        latitude === null &&
        longitude === null
    ) {

        return "";
    }


    return `
        <div class="location-info">

            ${
                region
                    ? `
                        <div>
                            <strong>
                                Region:
                            </strong>

                            ${escapeHTML(region)}
                        </div>
                      `
                    : ""
            }


            ${
                latitude !== null &&
                latitude !== undefined
                    ? `
                        <div>
                            <strong>
                                Latitude:
                            </strong>

                            ${escapeHTML(latitude)}
                        </div>
                      `
                    : ""
            }


            ${
                longitude !== null &&
                longitude !== undefined
                    ? `
                        <div>
                            <strong>
                                Longitude:
                            </strong>

                            ${escapeHTML(longitude)}
                        </div>
                      `
                    : ""
            }

        </div>
    `;
}


// ------------------------------------------------------------
// OVERALL ASSESSMENT
// ------------------------------------------------------------

function renderAssessment(
    response,
    analysis
) {

    if (
        response &&
        typeof response === "object" &&
        response.assessment
    ) {

        return `
            <p>
                ${escapeHTML(
                    response.assessment
                )}
            </p>
        `;
    }


    if (
        analysis &&
        typeof analysis === "object"
    ) {

        if (analysis.overall_assessment) {

            return `
                <p>
                    ${escapeHTML(
                        analysis.overall_assessment
                    )}
                </p>
            `;
        }


        if (analysis.assessment) {

            return `
                <p>
                    ${escapeHTML(
                        analysis.assessment
                    )}
                </p>
            `;
        }


        if (analysis.overall) {

            return `
                <p>
                    ${escapeHTML(
                        analysis.overall
                    )}
                </p>
            `;
        }
    }


    return `
        <p>
            No overall assessment was returned.
        </p>
    `;
}


// ------------------------------------------------------------
// DISPLAY ANALYSIS
// ------------------------------------------------------------

function displayAnalysis(data) {

    console.log(
        "Complete biodiversity API response:",
        data
    );


    const analysis =
        data.analysis || {};


    const response =
        data.response || {};


    // --------------------------------------------------------
    // OVERALL ASSESSMENT
    // --------------------------------------------------------

    const assessmentContainer =
        getElement(
            "assessment",
            "overallAssessment",
            "assessmentContent"
        );


    if (assessmentContainer) {

        assessmentContainer.innerHTML =
            renderAssessment(
                response,
                analysis
            );
    }


    // --------------------------------------------------------
    // FINDINGS
    // --------------------------------------------------------

    const findingsContainer =
        getElement(
            "findings",
            "keyFindings",
            "findingsContainer"
        );


    if (findingsContainer) {

        const findings =
            analysis.findings ||
            analysis.key_findings ||
            [];


        findingsContainer.innerHTML =
            renderFindings(findings);
    }


    // --------------------------------------------------------
    // INTERACTIONS
    // --------------------------------------------------------

    const interactionsContainer =
        getElement(
            "interactions",
            "multiMetricInteractions",
            "interactionsContainer"
        );


    if (interactionsContainer) {

        const interactions =
            response.key_interactions ||
            analysis.interactions ||
            [];


        interactionsContainer.innerHTML =
            renderInteractions(
                interactions
            );
    }


    // --------------------------------------------------------
    // RECOMMENDATIONS
    // --------------------------------------------------------

    const recommendationsContainer =
        getElement(
            "recommendations",
            "recommendationList",
            "recommendationsContainer"
        );


    if (recommendationsContainer) {

        const recommendations =
            response.recommendations ||
            analysis.recommendations ||
            [];


        recommendationsContainer.innerHTML =
            renderRecommendations(
                recommendations
            );
    }


    // --------------------------------------------------------
    // SCIENTIFIC EVIDENCE
    // --------------------------------------------------------

    const evidenceContainer =
        getElement(
            "scientificEvidence",
            "evidence",
            "evidenceContainer"
        );


    if (evidenceContainer) {

        const evidence =
            response.scientific_evidence ||
            data.scientific_evidence ||
            [];


        evidenceContainer.innerHTML =
            renderScientificEvidence(
                evidence
            );
    }


    // --------------------------------------------------------
    // LOCATION BIODIVERSITY
    // --------------------------------------------------------

    const gbifContainer =
        getElement(
            "locationBiodiversity",
            "gbifResults",
            "gbif",
            "locationBiodiversityContainer"
        );


    if (gbifContainer) {

        gbifContainer.innerHTML =
            renderLocationBiodiversity(
                data.location_biodiversity
            );
    }


    // --------------------------------------------------------
    // DATA LIMITATIONS
    // --------------------------------------------------------

    const limitationsContainer =
        getElement(
            "dataLimitations",
            "limitations",
            "limitationsContainer"
        );


    if (limitationsContainer) {

        const limitations =
            response.data_limitations ||
            data.data_quality?.warnings ||
            [];


        limitationsContainer.innerHTML =
            renderDataLimitations(
                limitations
            );
    }


    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    const locationContainer =
        getElement(
            "locationResult",
            "locationInfo",
            "locationDisplay"
        );


    if (locationContainer) {

        locationContainer.innerHTML =
            renderLocation(
                data.environment
            );
    }


    // --------------------------------------------------------
    // DATA QUALITY
    // --------------------------------------------------------

    const qualityContainer =
        getElement(
            "dataQuality",
            "quality"
        );


    if (
        qualityContainer &&
        data.data_quality
    ) {

        const quality =
            data.data_quality;


        qualityContainer.innerHTML = `
            <div class="data-quality">

                <strong>
                    Data completeness:
                </strong>

                ${escapeHTML(
                    safeValue(
                        quality.completeness_percent,
                        0
                    )
                )}%

            </div>
        `;
    }


    // --------------------------------------------------------
    // SHOW RESULTS
    // --------------------------------------------------------

    const resultsContainer =
        getElement(
            "results",
            "analysisResults",
            "resultsSection"
        );


    if (resultsContainer) {

        resultsContainer.style.display =
            "block";

        resultsContainer.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


// ------------------------------------------------------------
// ANALYZE ENVIRONMENT
// ------------------------------------------------------------

async function analyzeEnvironment() {

    const button =
        getElement(
            "analyzeBtn",
            "analyzeButton"
        );


    try {

        setLoading(
            button,
            true,
            "Analyzing..."
        );


        showStatus(
            "Analyzing environmental conditions...",
            "loading"
        );


        const environment =
            buildEnvironment();


        console.log(
            "Environment sent to backend:",
            environment
        );


        const question =
            getInputValue("question") ||
            "Analyze this environment and provide biodiversity recommendations.";


        const data =
            await apiRequest(
                "/analyze",
                "POST",
                {
                    question,
                    environment
                }
            );


        displayAnalysis(data);


        showStatus(
            "Biodiversity analysis completed successfully.",
            "success"
        );


    } catch (error) {

        console.error(
            "Biodiversity analysis error:",
            error
        );


        showStatus(
            error.message ||
            "Biodiversity analysis failed.",
            "error"
        );


        alert(
            "Biodiversity analysis failed:\n\n" +
            (
                error.message ||
                "Unknown error"
            )
        );


    } finally {

        setLoading(
            button,
            false
        );
    }
}


// ------------------------------------------------------------
// CHAT MESSAGE RENDERING
// ------------------------------------------------------------

function addChatMessage(
    role,
    message
) {

    const chatContainer =
        getElement(
            "chatMessages",
            "chatHistory",
            "messages"
        );


    if (!chatContainer) {
        return;
    }


    const messageDiv =
        document.createElement("div");


    messageDiv.className =
        `chat-message ${role}`;


    const content =
        typeof message === "object"
            ? (
                message.assessment ||
                JSON.stringify(message)
            )
            : message;


    messageDiv.innerHTML = `
        <div class="chat-bubble">

            ${escapeHTML(content)}

        </div>
    `;


    chatContainer.appendChild(
        messageDiv
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// ------------------------------------------------------------
// SEND CHAT MESSAGE
// ------------------------------------------------------------

async function sendChatMessage() {

    const input =
        getElement(
            "question",
            "chatInput",
            "messageInput"
        );


    const button =
        getElement(
            "sendButton",
            "sendChatBtn",
            "chatBtn",
            "sendButton"
        );


    if (!input) {

        console.error(
            "Chat input element not found."
        );

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


        input.value = "";


        setLoading(
            button,
            true,
            "Thinking..."
        );


        showStatus(
            "Processing your question...",
            "loading"
        );


        const environment =
            buildEnvironment();


        console.log(
            "Chat environment:",
            environment
        );


        const data =
            await apiRequest(
                "/chat",
                "POST",
                {
                    session_id: sessionId,
                    question,
                    environment
                }
            );


        const response =
            data.response || {};


        let assistantMessage =
            "";


        if (
            response &&
            typeof response === "object"
        ) {

            assistantMessage =
                response.assessment ||
                response.message ||
                "Analysis completed.";

        } else {

            assistantMessage =
                String(response);
        }


        addChatMessage(
            "assistant",
            assistantMessage
        );


        // Update the analysis sections as well

        displayAnalysis(data);


        showStatus(
            "Response generated successfully.",
            "success"
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


        showStatus(
            error.message ||
            "Chat request failed.",
            "error"
        );


    } finally {

        setLoading(
            button,
            false
        );
    }
}


// ------------------------------------------------------------
// CLEAR FORM
// ------------------------------------------------------------

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


    fieldIds.forEach((id) => {

        const element =
            document.getElementById(id);


        if (element) {

            element.value = "";
        }
    });


    // Clear result containers

    const resultIds = [

        "assessment",
        "overallAssessment",
        "assessmentContent",

        "findings",
        "keyFindings",
        "findingsContainer",

        "interactions",
        "multiMetricInteractions",
        "interactionsContainer",

        "recommendations",
        "recommendationList",
        "recommendationsContainer",

        "scientificEvidence",
        "evidence",
        "evidenceContainer",

        "locationBiodiversity",
        "gbifResults",
        "gbif",
        "locationBiodiversityContainer",

        "dataLimitations",
        "limitations",
        "limitationsContainer",

        "locationResult",
        "locationInfo",
        "locationDisplay",

        "dataQuality",
        "quality"
    ];


    resultIds.forEach((id) => {

        const element =
            document.getElementById(id);


        if (element) {

            element.innerHTML = "";
        }
    });


    const resultsContainer =
        getElement(
            "results",
            "analysisResults",
            "resultsSection"
        );


    if (resultsContainer) {

        resultsContainer.style.display =
            "none";
    }


    showStatus(
        "Form cleared.",
        "info"
    );
}


// ------------------------------------------------------------
// CLEAR CHAT
// ------------------------------------------------------------

function clearChat() {

    const chatContainer =
        getElement(
            "chatMessages",
            "chatHistory",
            "messages"
        );


    if (chatContainer) {

        chatContainer.innerHTML = "";
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


    showStatus(
        "Conversation cleared.",
        "info"
    );
}


// ------------------------------------------------------------
// SUGGESTION BUTTON
// ------------------------------------------------------------

function useSuggestion(text) {

    const input =
        getElement(
            "question",
            "chatInput",
            "messageInput"
        );


    if (!input) {
        return;
    }


    input.value = text;

    input.focus();
}


// ------------------------------------------------------------
// HEALTH CHECK
// ------------------------------------------------------------

async function checkBackend() {

    try {

        const data =
            await apiRequest(
                "/health",
                "GET"
            );


        console.log(
            "Darukaa backend:",
            data
        );


        showStatus(
            "Backend connected.",
            "success"
        );


    } catch (error) {

        console.warn(
            "Backend health check failed:",
            error
        );


        showStatus(
            "Backend connection unavailable.",
            "error"
        );
    }
}


// ------------------------------------------------------------
// EVENT LISTENERS
// ------------------------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "Darukaa.Earth frontend initialized."
        );


        console.log(
            "API:",
            API_BASE_URL
        );


        console.log(
            "Session:",
            sessionId
        );


        // ----------------------------------------------------
        // ANALYZE BUTTON
        // ----------------------------------------------------

        const analyzeButton =
            getElement(
                "analyzeBtn",
                "analyzeButton"
            );


        if (analyzeButton) {

            analyzeButton.addEventListener(
                "click",
                analyzeEnvironment
            );
        }


        // ----------------------------------------------------
        // SEND CHAT
        // ----------------------------------------------------

        const sendButton =
            getElement(
                "sendButton",
                "sendChatBtn",
                "chatBtn"
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
                "question",
                "chatInput",
                "messageInput"
            );


        if (questionInput) {

            questionInput.addEventListener(
                "keydown",
                (event) => {

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
                "clearBtn",
                "clearButton"
            );


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                clearForm
            );
        }


        // ----------------------------------------------------
        // CLEAR CHAT BUTTON
        // ----------------------------------------------------

        const clearChatButton =
            getElement(
                "clearChat",
                "clearChatBtn"
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
            (button) => {

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


        // ----------------------------------------------------
        // OPTIONAL BACKEND CHECK
        // ----------------------------------------------------

        checkBackend();

    }
);