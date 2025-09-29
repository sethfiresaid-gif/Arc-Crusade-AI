<?php
/**
 * Arc Crusade AI WordPress Integration
 * Voeg dit toe aan functions.php van je theme of child theme
 */

// Shortcode voor Arc Crusade AI
function arc_crusade_shortcode($atts) {
    $atts = shortcode_atts(array(
        'height' => '850',
        'width' => '100%',
        'title' => 'Arc Crusade AI',
        'subtitle' => 'Professional Manuscript Analysis Tool'
    ), $atts);
    
    $output = '
    <div class="arc-crusade-wrapper" style="width: ' . esc_attr($atts['width']) . '; height: ' . esc_attr($atts['height']) . 'px; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin: 20px auto; max-width: 1200px;">
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); color: white; padding: 25px 20px; text-align: center;">
            <h2 style="margin: 0 0 8px 0; font-size: 2.2em; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🏰 ' . esc_html($atts['title']) . '</h2>
            <p style="margin: 0 0 5px 0; font-size: 1.1em; opacity: 0.95;">' . esc_html($atts['subtitle']) . '</p>
            <small style="opacity: 0.8; font-size: 0.9em;">🔒 Private Access - Authorized Users Only</small>
        </div>
        <iframe 
            src="https://arc-crusade.streamlit.app/" 
            width="100%" 
            height="' . (intval($atts['height']) - 100) . '"
            style="border: none; display: block; background: #f8f9fa;"
            frameborder="0"
            scrolling="yes"
            allowfullscreen
            title="Arc Crusade AI - Manuscript Analyzer"
            loading="lazy">
        </iframe>
        <div style="background: #f8f9fa; padding: 12px 20px; text-align: center; color: #666; font-size: 0.85em; border-top: 1px solid #dee2e6;">
            <p style="margin: 0;">© 2025 Arc Crusade AI - Professional Manuscript Analysis</p>
        </div>
    </div>
    
    <style>
    .arc-crusade-wrapper {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    @media (max-width: 768px) {
        .arc-crusade-wrapper {
            height: 700px !important;
            margin: 10px auto !important;
            border-radius: 10px !important;
        }
        
        .arc-crusade-wrapper iframe {
            height: 580px !important;
        }
        
        .arc-crusade-wrapper h2 {
            font-size: 1.8em !important;
        }
    }
    
    @media (max-width: 480px) {
        .arc-crusade-wrapper {
            height: 600px !important;
        }
        
        .arc-crusade-wrapper iframe {
            height: 480px !important;
        }
    }
    </style>';
    
    return $output;
}
add_shortcode('arc_crusade', 'arc_crusade_shortcode');

// Admin menu voor Arc Crusade AI settings (optioneel)
function arc_crusade_admin_menu() {
    add_options_page(
        'Arc Crusade AI Settings',
        'Arc Crusade AI', 
        'manage_options',
        'arc-crusade-settings',
        'arc_crusade_settings_page'
    );
}
add_action('admin_menu', 'arc_crusade_admin_menu');

function arc_crusade_settings_page() {
    ?>
    <div class="wrap">
        <h1>🏰 Arc Crusade AI Settings</h1>
        
        <div class="card">
            <h2>Shortcode Gebruik</h2>
            <p>Gebruik deze shortcodes om Arc Crusade AI toe te voegen aan je pagina's:</p>
            
            <h3>Basis Shortcode:</h3>
            <code>[arc_crusade]</code>
            
            <h3>Met Custom Hoogte:</h3>
            <code>[arc_crusade height="900"]</code>
            
            <h3>Met Custom Titel:</h3>
            <code>[arc_crusade title="Mijn AI Tool" subtitle="Custom Subtitle"]</code>
            
            <h3>Alle Opties:</h3>
            <code>[arc_crusade height="850" width="100%" title="Arc Crusade AI" subtitle="Professional Manuscript Analysis Tool"]</code>
        </div>
        
        <div class="card">
            <h2>Direct HTML (voor Custom HTML blocks):</h2>
            <textarea rows="10" cols="80" readonly onclick="this.select()">
&lt;div style="width: 100%; height: 850px; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 25px rgba(0,0,0,0.15); margin: 20px 0;"&gt;
    &lt;div style="background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); color: white; padding: 20px; text-align: center;"&gt;
        &lt;h2 style="margin: 0 0 10px 0; font-size: 2em;"&gt;🏰 Arc Crusade AI&lt;/h2&gt;
        &lt;p style="margin: 0; opacity: 0.9;"&gt;Professional Manuscript Analysis Tool&lt;/p&gt;
    &lt;/div&gt;
    &lt;iframe src="https://arc-crusade.streamlit.app/" width="100%" height="780" style="border: none;"&gt;&lt;/iframe&gt;
&lt;/div&gt;
            </textarea>
        </div>
        
        <div class="card">
            <h2>App Status</h2>
            <p><strong>App URL:</strong> <a href="https://arc-crusade.streamlit.app/" target="_blank">https://arc-crusade.streamlit.app/</a></p>
            <p><strong>Status:</strong> <span style="color: green;">✅ Active</span></p>
        </div>
    </div>
    <?php
}

// Voeg CSS toe aan admin area
function arc_crusade_admin_styles() {
    ?>
    <style>
    .arc-crusade-wrapper code {
        background: #f1f1f1;
        padding: 4px 8px;
        border-radius: 4px;
        font-family: monospace;
        color: #d63384;
    }
    </style>
    <?php
}
add_action('admin_head', 'arc_crusade_admin_styles');
?>