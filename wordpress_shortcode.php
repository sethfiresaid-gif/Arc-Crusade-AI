// WordPress Shortcode voor Arc Crusade AI
// Voeg dit toe aan functions.php van je theme of child theme

function arc_crusade_embed_shortcode($atts) {
    $atts = shortcode_atts(array(
        'height' => '800',
        'width' => '100%'
    ), $atts);
    
    return '<div style="width: ' . $atts['width'] . '; height: ' . $atts['height'] . 'px; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin: 20px 0;">
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); color: white; padding: 20px; text-align: center;">
            <h2 style="margin: 0 0 10px 0; font-size: 1.8em;">🏰 Arc Crusade AI</h2>
            <p style="margin: 0; opacity: 0.9;">Professional Manuscript Analysis Tool</p>
        </div>
        <iframe src="https://arc-crusade.streamlit.app/" width="100%" height="' . ($atts['height'] - 100) . 'px" style="border: none; display: block;" frameborder="0"></iframe>
    </div>';
}
add_shortcode('arc_crusade', 'arc_crusade_embed_shortcode');

// Gebruik dan: [arc_crusade height="800"]