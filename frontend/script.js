// ============================================================
// DARUKAA.EARTH FRONTEND
// ============================================================

const API_URL = "http://127.0.0.1:8000";


// ============================================================
// SESSION
// ============================================================

let sessionId = localStorage.getItem("darukaa_session_id");

if (!sessionId) {
    sessionId =
        "session_" +
        Date.now() +
        "_" +
        Math.random()
            .toString(36)
            .substring(2, 9);

    localStorage.setItem(
        "darukaa_session_id",
        sessionId
    );
}


// ============================================================
// DOM HELPERS
// ============================================================

function getValue(id) {

    const element = document.getElementById(id);

    if (!element) {
        return null;
    }

    const value = element.value.trim();

    return value === "" ? null : value;
}


function getNumber(id) {

    const value = getValue(id);

    if (value === null) {
        return null;
    }

    const number = Number(value);

    return Number.isNaN(number)
        ? null
        : number;
}


// ============================================================
// BUILD ENVIRONMENT JSON
// ============================================================

function buildEnvironment() {

    return {

        soil: {

            ph: getNumber("ph"),

            organic_carbon_percent:
                getNumber(
                    "organic_carbon_percent"
                ),

            moisture_percent:
                getNumber(
                    "moisture_percent"
                )
        },

        climate: {

            rainfall_mm_year:
                getNumber(
                    "rainfall_mm_year"
                ),

            temperature_celsius:
                getNumber(
                    "temperature_celsius"
                )
        },

        land: {

            land_use:
                getValue("land_use"),

            crop_type:
                getValue("crop_type")
        },

        biodiversity: {

            species_richness:
                getValue(
                    "species_richness"
                ),

            habitat_diversity:
                getValue(
                    "habitat_diversity"
                )
        },

        human_impact: {

            pollution_level:
                getValue(
                    "pollution_level"
                ),

            deforestation_level:
                getValue(
                    "deforestation_level"
                ),

            habitat_fragmentation:
                getValue(
                    "habitat_fragmentation"
                )
        },

        location: {

            region:
                getValue("region"),

            latitude:
                getNumber("latitude"),

            longitude:
                getNumber("longitude")
        }
    };
}


// ============================================================
// DOM ELEMENTS
// ============================================================

const chatMessages =
    document.getElementById(
        "chatMessages"
    );

const questionInput =
    document.getElementById(
        "question"
    );

const sendButton =
    document.getElementById(
        "sendButton"
    );

const analyzeButton =
    document.getElementById(
        "analyzeButton"
    );

const clearButton =
    document.getElementById(
        "clearButton"
    );


// ============================================================
// ADD CHAT MESSAGE
// ============================================================

function addChatMessage(
    message,
    sender
) {

    if (!chatMessages) {
        return;
    }

    const messageDiv =
        document.createElement(
            "div"
        );

    messageDiv.className =
        `message ${sender}`;

    messageDiv.innerHTML =
        message;

    chatMessages.appendChild(
        messageDiv
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    if (value === null ||
        value === undefined) {

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
// SHOW LOADING
// ============================================================

function showLoading() {

    addChatMessage(
        `
        <div class="loading">
            Analyzing environmental data...
        </div>
        `,
        "assistant"
    );
}


// ============================================================
// FORMAT ASSESSMENT
// ============================================================

function formatAssessment(
    response
) {

    if (!response) {
        return "";
    }

    const assessment =
        response.assessment;

    if (!assessment) {
        return "";
    }

    return `
        <div class="result-section">
            <h3>🌿 Environmental Assessment</h3>
            <p>
                ${escapeHtml(assessment)}
            </p>
        </div>
    `;
}


// ============================================================
// FORMAT INTERACTIONS
// ============================================================

function formatInteractions(
    response
) {

    const interactions =
        response?.key_interactions;

    if (!Array.isArray(interactions) ||
        interactions.length === 0) {

        return "";
    }

    let html = `
        <div class="result-section">
            <h3>🔗 Key Environmental Interactions</h3>
    `;

    interactions.forEach(
        (item) => {

            html += `
                <div class="interaction-card">

                    <strong>
                        ${escapeHtml(
                            item.interaction
                        )}
                    </strong>

                    <p>
                        ${escapeHtml(
                            item.reasoning
                        )}
                    </p>

                </div>
            `;
        }
    );

    html += `</div>`;

    return html;
}


// ============================================================
// FORMAT RECOMMENDATIONS
// ============================================================

function formatRecommendations(
    response
) {

    const recommendations =
        response?.recommendations;

    if (!Array.isArray(recommendations) ||
        recommendations.length === 0) {

        return "";
    }

    let html = `
        <div class="result-section">

            <h3>
                🌱 Recommended Actions
            </h3>
    `;

    recommendations.forEach(
        (item, index) => {

            const metrics =
                Array.isArray(
                    item.impacted_metrics
                )
                    ? item.impacted_metrics
                    : [];

            html += `
                <div class="recommendation-card">

                    <h4>
                        ${index + 1}.
                        ${escapeHtml(
                            item.action
                        )}
                    </h4>

                    <p>
                        <strong>
                            Why it works:
                        </strong>

                        ${escapeHtml(
                            item.why_it_works
                        )}
                    </p>

                    <p>
                        <strong>
                            Impacted metrics:
                        </strong>

                        ${
                            metrics.length > 0
                                ? metrics
                                    .map(
                                        metric =>
                                            `<span class="metric">
                                                ${escapeHtml(metric)}
                                             </span>`
                                    )
                                    .join(" ")
                                : "Not specified"
                        }
                    </p>

                    <p>
                        <strong>
                            Time horizon:
                        </strong>

                        ${escapeHtml(
                            item.time_horizon
                        )}
                    </p>

                    <p>
                        <strong>
                            Confidence:
                        </strong>

                        ${escapeHtml(
                            item.confidence
                        )}
                    </p>

                </div>
            `;
        }
    );

    html += `</div>`;

    return html;
}


// ============================================================
// FORMAT SCIENTIFIC EVIDENCE
// ============================================================

function formatScientificEvidence(
    response
) {

    const evidence =
        response?.scientific_evidence;

    if (!Array.isArray(evidence) ||
        evidence.length === 0) {

        return "";
    }

    let html = `
        <div class="result-section">

            <h3>
                📚 Scientific Evidence
            </h3>
    `;

    evidence.forEach(
        (item) => {

            html += `
                <div class="evidence-card">

                    <strong>
                        ${escapeHtml(
                            item.source
                        )}
                    </strong>

                    ${
                        item.page
                            ? `
                                <span>
                                    Page:
                                    ${escapeHtml(
                                        item.page
                                    )}
                                </span>
                              `
                            : ""
                    }

                    <p>
                        ${escapeHtml(
                            item.evidence
                        )}
                    </p>

                </div>
            `;
        }
    );

    html += `</div>`;

    return html;
}


// ============================================================
// FORMAT GBIF DATA
// ============================================================

function formatGBIF(
    gbif
) {

    if (!gbif) {
        return "";
    }

    // --------------------------------------------------------
    // GBIF unavailable
    // --------------------------------------------------------

    if (!gbif.available) {

        return `
            <div class="result-section gbif-section">

                <h3>
                    🗺️ Location Biodiversity
                </h3>

                <div class="gbif-unavailable">

                    <p>
                        Location-based biodiversity
                        observations are currently unavailable.
                    </p>

                    ${
                        gbif.error
                            ? `
                                <small>
                                    ${escapeHtml(
                                        gbif.error
                                    )}
                                </small>
                              `
                            : ""
                    }

                </div>

            </div>
        `;
    }

    // --------------------------------------------------------
    // Available
    // --------------------------------------------------------

    const recordCount =
        gbif.record_count ?? 0;

    const returnedRecords =
        gbif.returned_records ?? 0;

    const observedTaxaCount =
        gbif.observed_taxa_count ?? 0;

    const taxa =
        Array.isArray(
            gbif.observed_taxa
        )
            ? gbif.observed_taxa
            : [];

    let taxaHTML = "";

    if (taxa.length > 0) {

        taxaHTML = `
            <div class="taxa-list">

                <strong>
                    Observed scientific names
                </strong>

                <ul>

                    ${
                        taxa
                            .slice(0, 20)
                            .map(
                                name =>
                                    `<li>
                                        ${escapeHtml(name)}
                                     </li>`
                            )
                            .join("")
                    }

                </ul>

            </div>
        `;

    } else {

        taxaHTML = `
            <p>
                No scientific names were returned
                in the retrieved records.
            </p>
        `;
    }

    return `
        <div class="result-section gbif-section">

            <h3>
                🗺️ Location Biodiversity
            </h3>

            <div class="gbif-summary">

                <div class="gbif-stat">

                    <strong>
                        ${escapeHtml(recordCount)}
                    </strong>

                    <span>
                        GBIF records
                    </span>

                </div>


                <div class="gbif-stat">

                    <strong>
                        ${escapeHtml(
                            returnedRecords
                        )}
                    </strong>

                    <span>
                        Retrieved
                    </span>

                </div>


                <div class="gbif-stat">

                    <strong>
                        ${escapeHtml(
                            observedTaxaCount
                        )}
                    </strong>

                    <span>
                        Observed taxa
                    </span>

                </div>

            </div>


            ${
                gbif.latitude !== undefined &&
                gbif.longitude !== undefined
                    ? `
                        <p>

                            <strong>
                                Location:
                            </strong>

                            ${escapeHtml(
                                gbif.latitude
                            )},
                            ${escapeHtml(
                                gbif.longitude
                            )}

                            <br>

                            <strong>
                                Search radius:
                            </strong>

                            ${escapeHtml(
                                gbif.radius_km
                            )} km

                        </p>
                      `
                    : ""
            }


            ${taxaHTML}


            <div class="gbif-note">

                <strong>
                    Important:
                </strong>

                GBIF occurrence records represent
                recorded observations available in GBIF.
                They are not a complete measure of true
                ecological species richness.

            </div>

        </div>
    `;
}


// ============================================================
// FORMAT DATA LIMITATIONS
// ============================================================

function formatLimitations(
    response
) {

    const limitations =
        response?.data_limitations;

    if (!Array.isArray(limitations) ||
        limitations.length === 0) {

        return "";
    }

    let html = `
        <div class="result-section">

            <h3>
                ⚠️ Data Limitations
            </h3>

            <ul class="limitations">
    `;

    limitations.forEach(
        limitation => {

            html += `
                <li>
                    ${escapeHtml(
                        limitation
                    )}
                </li>
            `;
        }
    );

    html += `
            </ul>
        </div>
    `;

    return html;
}


// ============================================================
// DISPLAY COMPLETE RESPONSE
// ============================================================

function displayResponse(
    data
) {

    const response =
        data?.response || {};

    let html = "";

    html += formatAssessment(
        response
    );

    html += formatInteractions(
        response
    );

    html += formatRecommendations(
        response
    );

    html += formatScientificEvidence(
        response
    );

    // GBIF DATA
    html += formatGBIF(
        data?.location_biodiversity
    );

    html += formatLimitations(
        response
    );

    if (!html) {

        html = `
            <div class="result-section">

                <p>
                    No structured response was returned.
                </p>

            </div>
        `;
    }

    addChatMessage(
        html,
        "assistant"
    );
}


// ============================================================
// SEND CHAT MESSAGE
// ============================================================

async function sendMessage() {

    const question =
        questionInput?.value.trim();

    if (!question) {

        return;
    }

    // --------------------------------------------------------
    // Display user message
    // --------------------------------------------------------

    addChatMessage(
        escapeHtml(question),
        "user"
    );

    // --------------------------------------------------------
    // Clear input
    // --------------------------------------------------------

    questionInput.value = "";

    // --------------------------------------------------------
    // Loading
    // --------------------------------------------------------

    showLoading();

    // --------------------------------------------------------
    // Environment
    // --------------------------------------------------------

    const environment =
        buildEnvironment();

    // --------------------------------------------------------
    // Request body
    // --------------------------------------------------------

    const requestBody = {

        session_id:
            sessionId,

        question:
            question,

        environment:
            environment
    };

    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        requestBody
                    )
                }
            );

        // ----------------------------------------------------
        // Remove loading message
        // ----------------------------------------------------

        removeLastLoadingMessage();

        // ----------------------------------------------------
        // HTTP error
        // ----------------------------------------------------

        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                `Server error ${response.status}: ${errorText}`
            );
        }

        // ----------------------------------------------------
        // Parse JSON
        // ----------------------------------------------------

        const data =
            await response.json();

        // ----------------------------------------------------
        // Display
        // ----------------------------------------------------

        displayResponse(
            data
        );

    } catch (error) {

        removeLastLoadingMessage();

        console.error(
            "Chat error:",
            error
        );

        addChatMessage(
            `
            <div class="error-message">

                <strong>
                    Could not connect to backend.
                </strong>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

                <small>
                    Make sure FastAPI is running on
                    http://127.0.0.1:8000
                </small>

            </div>
            `,
            "assistant"
        );
    }
}


// ============================================================
// REMOVE LAST LOADING MESSAGE
// ============================================================

function removeLastLoadingMessage() {

    if (!chatMessages) {
        return;
    }

    const messages =
        chatMessages.querySelectorAll(
            ".message.assistant"
        );

    if (messages.length === 0) {
        return;
    }

    const last =
        messages[messages.length - 1];

    if (
        last.querySelector(
            ".loading"
        )
    ) {

        last.remove();
    }
}


// ============================================================
// ANALYZE BUTTON
// ============================================================

async function analyzeEnvironment() {

    const environment =
        buildEnvironment();

    const question =
        questionInput?.value.trim() ||
        "Analyze this environment and recommend ways to improve biodiversity.";

    addChatMessage(
        `
            Analyzing the environmental profile...
        `,
        "user"
    );

    showLoading();

    try {

        const response =
            await fetch(
                `${API_URL}/analyze`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        environment:
                            environment
                    })
                }
            );

        removeLastLoadingMessage();

        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                `Server error ${response.status}: ${errorText}`
            );
        }

        const data =
            await response.json();

        displayResponse(
            data
        );

    } catch (error) {

        removeLastLoadingMessage();

        console.error(
            "Analyze error:",
            error
        );

        addChatMessage(
            `
                <div class="error-message">

                    <strong>
                        Analysis failed.
                    </strong>

                    <p>
                        ${escapeHtml(
                            error.message
                        )}
                    </p>

                </div>
            `,
            "assistant"
        );
    }
}


// ============================================================
// CLEAR FORM
// ============================================================

function clearEnvironment() {

    const fields = [

        "ph",

        "organic_carbon_percent",

        "moisture_percent",

        "rainfall_mm_year",

        "temperature_celsius",

        "land_use",

        "crop_type",

        "species_richness",

        "habitat_diversity",

        "pollution_level",

        "deforestation_level",

        "habitat_fragmentation",

        "region",

        "latitude",

        "longitude"
    ];

    fields.forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );

            if (element) {

                element.value = "";
            }
        }
    );

    if (chatMessages) {

        chatMessages.innerHTML = "";
    }

    addChatMessage(
        `
            Hello! Enter your environmental
            information and ask me a biodiversity
            question.
        `,
        "assistant"
    );
}


// ============================================================
// EVENT LISTENERS
// ============================================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendMessage
    );
}


if (analyzeButton) {

    analyzeButton.addEventListener(
        "click",
        analyzeEnvironment
    );
}


if (clearButton) {

    clearButton.addEventListener(
        "click",
        clearEnvironment
    );
}


// ============================================================
// ENTER KEY
// ============================================================

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();
            }
        }
    );
}


// ============================================================
// INITIAL MESSAGE
// ============================================================

if (chatMessages &&
    chatMessages.children.length === 0) {

    addChatMessage(
        `
            Hello! 👋

            I am the Darukaa.Earth Biodiversity
            Intelligence Assistant.

            Enter your environmental data and ask
            a question about biodiversity.
        `,
        "assistant"
    );
}