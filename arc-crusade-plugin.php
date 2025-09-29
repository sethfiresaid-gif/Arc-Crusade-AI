<?php
/**
 * Plugin Name: Arc Crusade AI Embed
 * Description: Embed Arc Crusade AI manuscript analyzer in your WordPress site
 * Version: 1.0
 * Author: Your Name
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class ArcCrusadePlugin {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_shortcode('arc_crusade', array($this, 'shortcode'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
    }
    
    public function init() {
        // Plugin initialization
    }
    
    public function shortcode($atts) {
        $atts = shortcode_atts(array(
            'height' => '850',
            'width' => '100%'
        ), $atts);
        
        return $this->render_iframe($atts);
    }
    
    private function render_iframe($atts) {
        ob_start();
        ?>
        <div class="arc-crusade-embed" style="width: <?php echo esc_attr($atts['width']); ?>; height: <?php echo esc_attr($atts['height']); ?>px; margin: 20px auto; max-width: 1200px;">
            <div class="arc-header">
                <h2>🏰 Arc Crusade AI</h2>
                <p>Professional Manuscript Analysis Tool</p>
            </div>
            <iframe 
                src="https://arc-crusade.streamlit.app/" 
                width="100%" 
                height="<?php echo intval($atts['height']) - 100; ?>"
                frameborder="0"
                allowfullscreen>
            </iframe>
        </div>
        <?php
        return ob_get_clean();
    }
    
    public function enqueue_styles() {
        wp_add_inline_style('arc-crusade-styles', '
            .arc-crusade-embed {
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            .arc-header {
                background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .arc-header h2 {
                margin: 0 0 10px 0;
                font-size: 2em;
            }
            .arc-header p {
                margin: 0;
                opacity: 0.9;
            }
        ');
    }
}

new ArcCrusadePlugin();
?>