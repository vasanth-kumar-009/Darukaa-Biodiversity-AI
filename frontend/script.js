// ============================================================
// DARUKAA.EARTH - BIODIVERSITY AI FRONTEND
// ============================================================

// Use the same Vercel deployment for the API.
// This also works when running the frontend locally.
const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : window.location.origin;


// ============================================================
// SESSION
// ============================================================

let sessionId = localStorage.getItem("darukaa_session_id");

if (!sessionId) {
    sessionId =
        "session_" +
        Date.now() +
        "_" +
        Math.random().toString(36).substring(2, 10);

    localStorage.setItem(
        "darukaa_session_id",
        sessionId
    );
}


// ============================================================
// DOM HELPERS
// ============================================================

function getElement(id) {
    return document.getElementById(id);
}

function getValue(id) {
    const element = getElement(id);

    if (!element) {
        return "";
    }

    return element.value.trim();
}

function getNumber(id) {
    const value = getValue(id);

    if (value === "") {
        return null;
    }

    const number = Number(value);

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
            ph: getNumber("ph"),

            organic_carbon_percent:
                getNumber("organicCarbon"),

            moisture_percent:
                getNumber("moisture")
        },

        climate: {
            rainfall_mm_year:
                getNumber("rainfall"),

            temperature_celsius:
                getNumber("temperature")
        },

        land: {
            land_use:
                getValue("landUse") || null,

            crop_type:
                getValue("cropType") || null
        },

        biodiversity: {
            species_richness:
                getValue("speciesRichness") || null,

            habitat_diversity:
                getValue("habitatDiversity") || null
        },

        human_impact: {
            pollution_level:
                getValue("pollutionLevel") || null,

            deforestation_level:
                getValue("deforestationLevel") || null,

            habitat_fragmentation:
                getValue("habitatFragmentation") || null
        },

        location: {
            latitude:
                getNumber("latitude"),

            longitude:
                getNumber("longitude"),

            region:
                getValue("region") || null
        }
    };
}


// ============================================================
// API REQUEST
// ============================================================

async function apiRequest(
    endpoint,
    options = {}
) {

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,

            headers: {
                "Content-Type": "application/json",

                ...(options.headers || {})
            }
        }
    );


    let data;

    try {

        data = await response.json();

    } catch (error) {

        throw new Error(
            `Server returned HTTP ${response.status}`
        );
    }


    if (!response.ok) {

        const message =
            data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}`;

        throw new Error(message);
    }


    return data;
}


// ============================================================
// LOADING STATE
// ============================================================

function setLoading(
    button,
    loading,
    originalText
) {

    if (!button) {
        return;
    }

    if (loading) {

        button.disabled = true;

        button.dataset.originalText =
            originalText ||
            button.textContent;

        button.textContent =
            "Analyzing...";

    } else {

        button.disabled = false;

        button.textContent =
            button.dataset.originalText ||
            originalText ||
            "Analyze";
    }
}


// ============================================================
// RESULT ELEMENT
// ============================================================

function getResultsContainer() {

    return (
        getElement("results") ||
        getElement("resultContainer") ||
        getElement("resultsContainer")
    );
}


// ============================================================
// SAFE TEXT
// ============================================================

function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ============================================================
// RENDER ANALYSIS
// ============================================================

function renderAnalysis(data) {

    const container =
        getResultsContainer();

    if (!container) {
        console.warn(
            "Results container not found."
        );
        return;
    }


    const response =
        data.response || {};

    const analysis =
        data.analysis || {};

    const findings =
        analysis.findings || [];

    const interactions =
        response.key_interactions ||
        analysis.interactions ||
        [];

    const recommendations =
        response.recommendations ||
        [];

    const evidence =
        response.scientific_evidence ||
        data.scientific_evidence ||
        [];

    const limitations =
        response.data_limitations ||
        [];

    const gbif =
        data.location_biodiversity ||
        null;


    let html = "";


    // ========================================================
    // ASSESSMENT
    // ========================================================

    html += `
        <section class="result-card assessment-card">

            <h2>Environmental Assessment</h2>

            <p>
                ${escapeHTML(
                    response.assessment ||
                    analysis.overall_assessment ||
                    "No assessment available."
                )}
            </p>

        </section>
    `;


    // ========================================================
    // FINDINGS
    // ========================================================

    if (findings.length > 0) {

        html += `
            <section class="result-card">

                <h2>Environmental Findings</h2>

                <div class="finding-list">
        `;

        findings.forEach(
            (finding) => {

                html += `
                    <div class="finding-item">

                        <h3>
                            ${escapeHTML(
                                finding.factor
                            )}
                        </h3>

                        <span class="severity">
                            ${escapeHTML(
                                finding.severity
                            )}
                        </span>

                        <p>
                            ${escapeHTML(
                                finding.explanation
                            )}
                        </p>

                    </div>
                `;
            }
        );

        html += `
                </div>
            </section>
        `;
    }


    // ========================================================
    // KEY INTERACTIONS
    // ========================================================

    if (interactions.length > 0) {

        html += `
            <section class="result-card">

                <h2>Multi-Metric Interactions</h2>

                <div class="interaction-list">
        `;

        interactions.forEach(
            (item) => {

                const title =
                    item.interaction ||
                    (
                        Array.isArray(item.variables)
                            ? item.variables.join(" + ")
                            : "Environmental interaction"
                    );

                html += `
                    <div class="interaction-item">

                        <h3>
                            ${escapeHTML(title)}
                        </h3>

                        <p>
                            ${escapeHTML(
                                item.reasoning ||
                                "No reasoning provided."
                            )}
                        </p>

                    </div>
                `;
            }
        );

        html += `
                </div>
            </section>
        `;
    }


    // ========================================================
    // RECOMMENDATIONS
    // ========================================================

    if (recommendations.length > 0) {

        html += `
            <section class="result-card">

                <h2>Biodiversity Recommendations</h2>

                <div class="recommendation-list">
        `;

        recommendations.forEach(
            (recommendation, index) => {

                const metrics =
                    recommendation.impacted_metrics ||
                    [];

                html += `
                    <article class="recommendation-card">

                        <div class="recommendation-number">
                            ${index + 1}
                        </div>

                        <div class="recommendation-content">

                            <h3>
                                ${escapeHTML(
                                    recommendation.action ||
                                    "Recommended action"
                                )}
                            </h3>

                            <p>
                                <strong>Why it works:</strong>
                                ${escapeHTML(
                                    recommendation.why_it_works ||
                                    ""
                                )}
                            </p>

                            ${
                                metrics.length > 0
                                    ? `
                                    <p>
                                        <strong>Impacted metrics:</strong>
                                        ${metrics
                                            .map(
                                                metric =>
                                                    `<span class="metric-tag">
                                                        ${escapeHTML(metric)}
                                                    </span>`
                                            )
                                            .join(" ")}
                                    </p>
                                    `
                                    : ""
                            }

                            <p>
                                <strong>Time horizon:</strong>
                                ${escapeHTML(
                                    recommendation.time_horizon ||
                                    "Not specified"
                                )}
                            </p>

                            <p>
                                <strong>Confidence:</strong>
                                ${escapeHTML(
                                    recommendation.confidence ||
                                    "Not specified"
                                )}
                            </p>

                        </div>

                    </article>
                `;
            }
        );

        html += `
                </div>
            </section>
        `;
    }


    // ========================================================
    // SCIENTIFIC EVIDENCE
    // ========================================================

    if (evidence.length > 0) {

        html += `
            <section class="result-card">

                <h2>Scientific Evidence</h2>

                <div class="evidence-list">
        `;

        evidence.forEach(
            (item) => {

                html += `
                    <article class="evidence-card">

                        <h3>
                            ${escapeHTML(
                                item.source ||
                                "Scientific source"
                            )}
                        </h3>

                        <p>
                            <strong>Page:</strong>
                            ${escapeHTML(
                                item.page ||
                                "Not specified"
                            )}
                        </p>

                        <p>
                            ${escapeHTML(
                                item.evidence ||
                                item.text ||
                                ""
                            )}
                        </p>

                    </article>
                `;
            }
        );

        html += `
                </div>
            </section>
        `;
    }


    // ========================================================
    // GBIF
    // ========================================================

    if (
        gbif &&
        gbif.available
    ) {

        const taxa =
            gbif.observed_taxa || [];

        html += `
            <section class="result-card gbif-card">

                <h2>Location Biodiversity — GBIF</h2>

                <div class="gbif-summary">

                    <div>
                        <strong>
                            ${escapeHTML(
                                gbif.record_count || 0
                            )}
                        </strong>

                        <span>
                            occurrence records
                        </span>
                    </div>

                    <div>
                        <strong>
                            ${escapeHTML(
                                gbif.observed_taxa_count || 0
                            )}
                        </strong>

                        <span>
                            observed taxa
                        </span>
                    </div>

                    <div>
                        <strong>
                            ${escapeHTML(
                                gbif.radius_km || 0
                            )} km
                        </strong>

                        <span>
                            search radius
                        </span>
                    </div>

                </div>
        `;


        if (taxa.length > 0) {

            html += `
                <h3>Observed Taxa</h3>

                <ul class="taxa-list">
            `;

            taxa.slice(0, 20).forEach(
                (taxon) => {

                    html += `
                        <li>
                            ${escapeHTML(taxon)}
                        </li>
                    `;
                }
            );

            html += `
                </ul>
            `;
        }


        html += `
                <p class="data-note">

                    GBIF occurrence records represent
                    recorded observations and should not
                    be interpreted as a complete measure
                    of true species richness or species absence.

                </p>

            </section>
        `;
    }


    // ========================================================
    // DATA LIMITATIONS
    // ========================================================

    if (limitations.length > 0) {

        html += `
            <section class="result-card limitation-card">

                <h2>Data Limitations</h2>

                <ul>
        `;

        limitations.forEach(
            (limitation) => {

                html += `
                    <li>
                        ${escapeHTML(
                            limitation
                        )}
                    </li>
                `;
            }
        );

        html += `
                </ul>

            </section>
        `;
    }


    container.innerHTML = html;


    // Scroll to results

    container.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ============================================================
// ANALYZE
// ============================================================

async function analyzeEnvironment() {

    const button =
        getElement("analyzeBtn") ||
        getElement("analyzeButton");

    const question =
        getValue("question") ||
        getValue("userQuestion");


    if (!question) {

        alert(
            "Please enter a biodiversity question."
        );

        return;
    }


    const environment =
        buildEnvironment();


    setLoading(
        button,
        true
    );


    try {

        const data =
            await apiRequest(
                "/analyze",
                {
                    method: "POST",

                    body: JSON.stringify({
                        question,
                        environment
                    })
                }
            );


        renderAnalysis(data);


    } catch (error) {

        console.error(
            "Analyze error:",
            error
        );


        alert(
            "Analysis failed:\n\n" +
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
// CHAT
// ============================================================

async function sendChatMessage() {

    const input =
        getElement("chatInput") ||
        getElement("chatMessage") ||
        getElement("message");

    const chatContainer =
        getElement("chatMessages") ||
        getElement("chatHistory");


    if (!input) {

        console.error(
            "Chat input not found."
        );

        return;
    }


    const question =
        input.value.trim();


    if (!question) {
        return;
    }


    // --------------------------------------------------------
    // Add user message
    // --------------------------------------------------------

    if (chatContainer) {

        const userMessage =
            document.createElement("div");

        userMessage.className =
            "chat-message user-message";

        userMessage.textContent =
            question;

        chatContainer.appendChild(
            userMessage
        );

        chatContainer.scrollTop =
            chatContainer.scrollHeight;
    }


    input.value = "";


    // --------------------------------------------------------
    // Build environment
    // --------------------------------------------------------

    const environment =
        buildEnvironment();


    try {

        const data =
            await apiRequest(
                "/chat",
                {
                    method: "POST",

                    body: JSON.stringify({

                        session_id:
                            sessionId,

                        question,

                        environment
                    })
                }
            );


        // ----------------------------------------------------
        // Add assistant message
        // ----------------------------------------------------

        if (chatContainer) {

            const assistantMessage =
                document.createElement("div");

            assistantMessage.className =
                "chat-message assistant-message";


            const response =
                data.response || {};


            assistantMessage.innerHTML = `

                <strong>
                    Darukaa AI
                </strong>

                <p>
                    ${escapeHTML(
                        response.assessment ||
                        "Analysis completed."
                    )}
                </p>

            `;


            chatContainer.appendChild(
                assistantMessage
            );


            chatContainer.scrollTop =
                chatContainer.scrollHeight;
        }


        // Also update detailed results

        renderAnalysis(data);


    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        if (chatContainer) {

            const errorMessage =
                document.createElement("div");

            errorMessage.className =
                "chat-message error-message";

            errorMessage.textContent =
                "Error: " +
                error.message;

            chatContainer.appendChild(
                errorMessage
            );
        }
    }
}


// ============================================================
// CLEAR
// ============================================================

function clearConversation() {

    const chatContainer =
        getElement("chatMessages") ||
        getElement("chatHistory");

    const results =
        getResultsContainer();


    if (chatContainer) {

        chatContainer.innerHTML = "";
    }


    if (results) {

        results.innerHTML = "";
    }


    // New session

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
// EVENT LISTENERS
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const analyzeButton =
            getElement("analyzeBtn") ||
            getElement("analyzeButton");


        if (analyzeButton) {

            analyzeButton.addEventListener(
                "click",
                analyzeEnvironment
            );
        }


        const chatButton =
            getElement("chatBtn") ||
            getElement("sendChatBtn") ||
            getElement("sendButton");


        if (chatButton) {

            chatButton.addEventListener(
                "click",
                sendChatMessage
            );
        }


        const clearButton =
            getElement("clearBtn") ||
            getElement("clearButton");


        if (clearButton) {

            clearButton.addEventListener(
                "click",
                clearConversation
            );
        }


        const chatInput =
            getElement("chatInput") ||
            getElement("chatMessage") ||
            getElement("message");


        if (chatInput) {

            chatInput.addEventListener(
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

    }
);