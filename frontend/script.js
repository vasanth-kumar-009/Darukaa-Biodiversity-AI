/* =========================================================
   DARUKAA.EARTH FRONTEND
========================================================= */


/* =========================================================
   API URL
========================================================= */

const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : window.location.origin;


/* =========================================================
   SESSION
========================================================= */

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


/* =========================================================
   GET ELEMENT
========================================================= */

function getElement(id) {
    return document.getElementById(id);
}


/* =========================================================
   BUILD ENVIRONMENT
========================================================= */

function buildEnvironment() {

    return {

        soil: {

            ph:
                getElement("ph").value !== ""
                    ? Number(getElement("ph").value)
                    : null,

            organic_carbon_percent:
                getElement("organicCarbon").value !== ""
                    ? Number(getElement("organicCarbon").value)
                    : null,

            moisture_percent:
                getElement("moisture").value !== ""
                    ? Number(getElement("moisture").value)
                    : null
        },


        climate: {

            rainfall_mm_year:
                getElement("rainfall").value !== ""
                    ? Number(getElement("rainfall").value)
                    : null,

            temperature_celsius:
                getElement("temperature").value !== ""
                    ? Number(getElement("temperature").value)
                    : null
        },


        land: {

            land_use:
                getElement("landUse").value.trim() || null,

            crop_type:
                getElement("cropType").value.trim() || null
        },


        biodiversity: {

            species_richness:
                getElement("speciesRichness").value || null,

            habitat_diversity:
                getElement("habitatDiversity").value || null
        },


        human_impact: {

            pollution_level:
                getElement("pollutionLevel").value || null,

            deforestation_level:
                getElement("deforestationLevel").value || null,

            habitat_fragmentation:
                getElement("habitatFragmentation").value || null
        },


        location: {

            latitude:
                getElement("latitude").value !== ""
                    ? Number(getElement("latitude").value)
                    : null,

            longitude:
                getElement("longitude").value !== ""
                    ? Number(getElement("longitude").value)
                    : null,

            region:
                getElement("region").value.trim() || null
        }

    };
}


/* =========================================================
   API REQUEST
========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            },

            ...options
        }
    );


    let data;

    try {

        data = await response.json();

    } catch {

        throw new Error(
            "Server returned an invalid response."
        );

    }


    if (!response.ok) {

        let message =
            data.detail ||
            data.message ||
            "Request failed.";

        if (Array.isArray(data.detail)) {

            message =
                data.detail
                    .map(error =>
                        error.msg || "Validation error"
                    )
                    .join(", ");
        }

        throw new Error(message);
    }


    return data;
}


/* =========================================================
   LOADING
========================================================= */

function showLoading(button, text) {

    if (!button) return;

    button.dataset.originalText =
        button.innerHTML;

    button.disabled = true;

    button.innerHTML =
        `⏳ ${text}`;
}


function hideLoading(button) {

    if (!button) return;

    button.disabled = false;

    if (button.dataset.originalText) {

        button.innerHTML =
            button.dataset.originalText;
    }
}


/* =========================================================
   ESCAPE HTML
========================================================= */

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


/* =========================================================
   ANALYSIS
========================================================= */

async function analyzeEnvironment() {

    const button =
        getElement("analyzeBtn");

    const results =
        getElement("analysisResults");

    const content =
        getElement("resultsContent");


    showLoading(
        button,
        "Analyzing..."
    );


    results.style.display = "block";

    content.innerHTML = `
        <div class="message assistant">
            <strong>Darukaa.Earth</strong>
            <p>
                Analyzing environmental conditions,
                scientific evidence and biodiversity context...
            </p>
        </div>
    `;


    try {

        const environment =
            buildEnvironment();


        const data =
            await apiRequest(
                "/analyze",
                {
                    method: "POST",

                    body: JSON.stringify({

                        question:
                            "Analyze this environment and provide biodiversity recommendations.",

                        environment:
                            environment
                    })
                }
            );


        renderAnalysis(data);


    } catch (error) {

        content.innerHTML = `
            <div class="message assistant">

                <strong>Error</strong>

                <p>
                    ${escapeHTML(error.message)}
                </p>

            </div>
        `;

    } finally {

        hideLoading(button);

    }
}


/* =========================================================
   RENDER ANALYSIS
========================================================= */

function renderAnalysis(data) {

    const results =
        getElement("analysisResults");

    const content =
        getElement("resultsContent");


    const analysis =
        data.analysis || {};

    const response =
        data.response || {};


    let html = "";


    /* Assessment */

    if (
        response.assessment ||
        analysis.overall_assessment
    ) {

        html += `

            <div class="section">

                <h3>🌍 Overall Assessment</h3>

                <p>
                    ${escapeHTML(
                        response.assessment ||
                        analysis.overall_assessment
                    )}
                </p>

            </div>

        `;
    }


    /* Findings */

    if (
        Array.isArray(analysis.findings) &&
        analysis.findings.length > 0
    ) {

        html += `
            <div class="section">

                <h3>🔎 Key Environmental Findings</h3>

                <ul>
        `;


        analysis.findings.forEach(
            finding => {

                html += `
                    <li>
                        ${escapeHTML(finding)}
                    </li>
                `;

            }
        );


        html += `
                </ul>

            </div>
        `;
    }


    /* Interactions */

    const interactions =
        response.key_interactions ||
        analysis.interactions ||
        [];


    if (
        Array.isArray(interactions) &&
        interactions.length > 0
    ) {

        html += `

            <div class="section">

                <h3>🔗 Multi-Metric Interactions</h3>

        `;


        interactions.forEach(
            interaction => {

                if (
                    typeof interaction === "object"
                ) {

                    html += `

                        <div class="message assistant">

                            <strong>
                                ${escapeHTML(
                                    interaction.interaction ||
                                    "Environmental interaction"
                                )}
                            </strong>

                            <p>
                                ${escapeHTML(
                                    interaction.reasoning ||
                                    ""
                                )}
                            </p>

                        </div>

                    `;

                } else {

                    html += `

                        <div class="message assistant">

                            <p>
                                ${escapeHTML(interaction)}
                            </p>

                        </div>

                    `;
                }

            }
        );


        html += `</div>`;
    }


    /* Recommendations */

    const recommendations =
        response.recommendations ||
        analysis.recommendations ||
        [];


    if (
        Array.isArray(recommendations) &&
        recommendations.length > 0
    ) {

        html += `

            <div class="section">

                <h3>🌱 Recommendations</h3>

        `;


        recommendations.forEach(
            recommendation => {

                if (
                    typeof recommendation === "object"
                ) {

                    html += `

                        <div class="message assistant">

                            <strong>
                                ${escapeHTML(
                                    recommendation.action ||
                                    "Recommended action"
                                )}
                            </strong>

                            <p>
                                <strong>Why it works:</strong>
                                ${escapeHTML(
                                    recommendation.why_it_works ||
                                    ""
                                )}
                            </p>

                            <p>
                                <strong>Impacted metrics:</strong>
                                ${escapeHTML(
                                    Array.isArray(
                                        recommendation.impacted_metrics
                                    )
                                        ? recommendation.impacted_metrics.join(", ")
                                        : recommendation.impacted_metrics || ""
                                )}
                            </p>

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

                    `;

                } else {

                    html += `

                        <div class="message assistant">

                            <p>
                                ${escapeHTML(recommendation)}
                            </p>

                        </div>

                    `;
                }

            }
        );


        html += `</div>`;
    }


    /* Scientific Evidence */

    const evidence =
        response.scientific_evidence ||
        data.scientific_evidence ||
        [];


    if (
        Array.isArray(evidence) &&
        evidence.length > 0
    ) {

        html += `

            <div class="section">

                <h3>🔬 Scientific Evidence</h3>

        `;


        evidence.forEach(
            item => {

                if (
                    typeof item === "object"
                ) {

                    html += `

                        <div class="message assistant">

                            <strong>
                                ${escapeHTML(
                                    item.source ||
                                    "Scientific source"
                                )}
                            </strong>

                            <p>
                                ${
                                    item.page
                                        ? `Page: ${escapeHTML(item.page)}`
                                        : ""
                                }
                            </p>

                            <p>
                                ${escapeHTML(
                                    item.evidence ||
                                    item.text ||
                                    ""
                                )}
                            </p>

                        </div>

                    `;

                } else {

                    html += `

                        <div class="message assistant">

                            <p>
                                ${escapeHTML(item)}
                            </p>

                        </div>

                    `;
                }

            }
        );


        html += `</div>`;
    }


    /* GBIF */

    const gbif =
        data.location_biodiversity;


    if (gbif) {

        html += `

            <div class="section">

                <h3>📍 Location Biodiversity</h3>

                <p>
                    Nearby biodiversity observations:
                    <strong>
                        ${escapeHTML(
                            gbif.total_records ?? "N/A"
                        )}
                    </strong>
                </p>

                <p>
                    Observed taxa:
                    <strong>
                        ${escapeHTML(
                            gbif.unique_taxa ?? "N/A"
                        )}
                    </strong>
                </p>

                <p>
                    These observations provide geographic
                    biodiversity context and should not be
                    interpreted as complete species richness.
                </p>

            </div>

        `;
    }


    /* Data limitations */

    const limitations =
        response.data_limitations ||
        [];


    if (
        Array.isArray(limitations) &&
        limitations.length > 0
    ) {

        html += `

            <div class="section">

                <h3>⚠️ Data Limitations</h3>

                <ul>
        `;


        limitations.forEach(
            limitation => {

                html += `
                    <li>
                        ${escapeHTML(limitation)}
                    </li>
                `;

            }
        );


        html += `
                </ul>

            </div>
        `;
    }


    if (!html) {

        html = `

            <div class="message assistant">

                <strong>Darukaa.Earth</strong>

                <p>
                    Analysis completed, but no formatted
                    result was returned.
                </p>

            </div>

        `;
    }


    content.innerHTML = html;

    results.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/* =========================================================
   CHAT
========================================================= */

async function sendChatMessage() {

    const input =
        getElement("question");

    const button =
        getElement("sendButton");

    const messages =
        getElement("chatMessages");


    const question =
        input.value.trim();


    if (!question) {

        input.focus();

        return;
    }


    const environment =
        buildEnvironment();


    /* User message */

    messages.innerHTML += `

        <div class="message user">

            <strong>You</strong>

            <p>
                ${escapeHTML(question)}
            </p>

        </div>

    `;


    input.value = "";


    /* Loading */

    messages.innerHTML += `

        <div
            id="chatLoading"
            class="message assistant"
        >

            <strong>Darukaa.Earth</strong>

            <p>
                Thinking...
            </p>

        </div>

    `;


    messages.scrollTop =
        messages.scrollHeight;


    showLoading(
        button,
        "Sending..."
    );


    try {

        const data =
            await apiRequest(
                "/chat",
                {
                    method: "POST",

                    body: JSON.stringify({

                        session_id:
                            sessionId,

                        question:
                            question,

                        environment:
                            environment
                    })
                }
            );


        const loading =
            getElement("chatLoading");

        if (loading) {
            loading.remove();
        }


        renderChatResponse(data);


    } catch (error) {

        const loading =
            getElement("chatLoading");

        if (loading) {
            loading.remove();
        }


        messages.innerHTML += `

            <div class="message assistant">

                <strong>Error</strong>

                <p>
                    ${escapeHTML(error.message)}
                </p>

            </div>

        `;

    } finally {

        hideLoading(button);

        messages.scrollTop =
            messages.scrollHeight;
    }
}


/* =========================================================
   CHAT RESPONSE
========================================================= */

function renderChatResponse(data) {

    const messages =
        getElement("chatMessages");


    const response =
        data.response || {};


    let text = "";


    if (
        typeof response === "string"
    ) {

        text = response;

    } else {

        if (response.assessment) {

            text +=
                `<strong>Assessment:</strong><br>${escapeHTML(response.assessment)}<br><br>`;
        }


        if (
            Array.isArray(
                response.recommendations
            )
        ) {

            text +=
                "<strong>Recommendations:</strong><br>";


            response.recommendations.forEach(
                recommendation => {

                    if (
                        typeof recommendation === "object"
                    ) {

                        text +=
                            `• ${escapeHTML(
                                recommendation.action ||
                                ""
                            )}<br>`;

                    } else {

                        text +=
                            `• ${escapeHTML(
                                recommendation
                            )}<br>`;
                    }

                }
            );
        }


        if (
            Array.isArray(
                response.key_interactions
            )
        ) {

            text +=
                "<br><strong>Key interactions:</strong><br>";


            response.key_interactions.forEach(
                interaction => {

                    if (
                        typeof interaction === "object"
                    ) {

                        text +=
                            `• ${escapeHTML(
                                interaction.interaction ||
                                ""
                            )}: ${escapeHTML(
                                interaction.reasoning ||
                                ""
                            )}<br>`;

                    } else {

                        text +=
                            `• ${escapeHTML(
                                interaction
                            )}<br>`;
                    }

                }
            );
        }

    }


    if (!text) {

        text =
            "I completed the analysis but could not format the response.";
    }


    messages.innerHTML += `

        <div class="message assistant">

            <strong>Darukaa.Earth</strong>

            <p>
                ${text}
            </p>

        </div>

    `;
}


/* =========================================================
   CLEAR FORM
========================================================= */

function clearEnvironment() {

    const ids = [

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
        "longitude"
    ];


    ids.forEach(id => {

        const element =
            getElement(id);

        if (!element) return;

        element.value = "";

    });


    const results =
        getElement("analysisResults");


    if (results) {

        results.style.display =
            "none";
    }
}


/* =========================================================
   EVENT LISTENERS
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const analyzeButton =
            getElement("analyzeBtn");

        const clearButton =
            getElement("clearBtn");

        const sendButton =
            getElement("sendButton");

        const questionInput =
            getElement("question");


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


        if (sendButton) {

            sendButton.addEventListener(
                "click",
                sendChatMessage
            );
        }


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


        /* Suggestion buttons */

        document
            .querySelectorAll(
                ".message-suggestions button"
            )
            .forEach(button => {

                button.addEventListener(
                    "click",
                    () => {

                        if (!questionInput) {
                            return;
                        }

                        questionInput.value =
                            button.textContent.trim();

                        questionInput.focus();
                    }
                );

            });

    }
);