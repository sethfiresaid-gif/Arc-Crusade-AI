# WordPress API Integration (OPTIONEEL - niet vereist voor iframe)
# Dit is alleen nodig als je WordPress data naar Streamlit wilt sturen

# WordPress REST API endpoint (als je het wilt)
# Voeg toe aan functions.php:

function arc_crusade_api_endpoint() {
    register_rest_route('arc-crusade/v1', '/submit-manuscript', array(
        'methods' => 'POST',
        'callback' => 'handle_manuscript_submission',
        'permission_callback' => '__return_true'
    ));
}
add_action('rest_api_init', 'arc_crusade_api_endpoint');

function handle_manuscript_submission($request) {
    $manuscript_data = $request->get_json_params();
    
    // Doorsturen naar Streamlit app
    $response = wp_remote_post('https://arc-crusade.streamlit.app/api/process', array(
        'body' => json_encode($manuscript_data),
        'headers' => array('Content-Type' => 'application/json')
    ));
    
    return rest_ensure_response($response);
}

# MAAR DIT IS NIET NODIG VOOR IFRAME EMBEDDING!