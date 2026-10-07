<?php
/**
 * UTALK Center theme setup.
 *
 * @package utalk
 */

defined( 'ABSPATH' ) || exit;

define( 'UTALK_VERSION', '{{VERSION}}' );

require get_template_directory() . '/inc/pages.php';

/* ---------------------------------------------------------------------------
 * Theme supports
 * ------------------------------------------------------------------------ */
add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'title-tag' );
		add_theme_support( 'post-thumbnails' );
		add_theme_support( 'responsive-embeds' );
		add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );

		add_theme_support(
			'woocommerce',
			array(
				'thumbnail_image_width' => 600,
				'single_image_width'    => 900,
			)
		);
		add_theme_support( 'wc-product-gallery-zoom' );
		add_theme_support( 'wc-product-gallery-lightbox' );
		add_theme_support( 'wc-product-gallery-slider' );
	}
);

add_filter(
	'document_title_separator',
	function () {
		return '·';
	}
);

/* ---------------------------------------------------------------------------
 * Assets
 * ------------------------------------------------------------------------ */
add_action(
	'wp_enqueue_scripts',
	function () {
		wp_enqueue_style( 'utalk', get_theme_file_uri( 'assets/css/style.css' ), array(), UTALK_VERSION );
		wp_enqueue_style( 'utalk-wp', get_theme_file_uri( 'assets/css/wp.css' ), array( 'utalk' ), UTALK_VERSION );
		wp_enqueue_script( 'utalk', get_theme_file_uri( 'assets/js/main.js' ), array(), UTALK_VERSION, true );
	}
);

add_action(
	'wp_head',
	function () {
		$fonts = array( 'CabinetGrotesk-700', 'CabinetGrotesk-500' );
		foreach ( $fonts as $font ) {
			printf( '<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n", esc_url( get_theme_file_uri( "assets/fonts/$font.woff2" ) ) );
		}

		if ( ! has_site_icon() ) {
			printf( '<link rel="icon" href="%s" sizes="any">' . "\n", esc_url( get_theme_file_uri( 'assets/img/favicon.ico' ) ) );
			printf( '<link rel="icon" type="image/png" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/img/favicon-32.png' ) ) );
			printf( '<link rel="apple-touch-icon" href="%s">' . "\n", esc_url( get_theme_file_uri( 'assets/img/apple-touch-icon.png' ) ) );
		}

		// Leave descriptions to an SEO plugin when one is active.
		if ( defined( 'WPSEO_VERSION' ) || defined( 'RANK_MATH_VERSION' ) || defined( 'AIOSEO_VERSION' ) || defined( 'SEOPRESS_VERSION' ) ) {
			return;
		}
		$desc = utalk_current_description();
		if ( $desc ) {
			printf( '<meta name="description" content="%s">' . "\n", esc_attr( $desc ) );
		}
	},
	2
);

/* ---------------------------------------------------------------------------
 * Links between the theme's pages
 * ------------------------------------------------------------------------ */

/**
 * URL of one of the theme's pages, by path ('' = home, 'langues/english', …).
 * Falls back to the pretty URL if the page was deleted.
 */
function utalk_url( $path = '', $hash = '' ) {
	static $cache = array();

	if ( '' === $path ) {
		return home_url( '/' ) . $hash;
	}
	if ( ! isset( $cache[ $path ] ) ) {
		$page           = get_page_by_path( $path );
		$cache[ $path ] = $page ? get_permalink( $page ) : home_url( '/' . $path . '/' );
	}
	return $cache[ $path ] . $hash;
}

/** Print aria-current on the navbar link of the page being viewed (or its parent). */
function utalk_current( $path ) {
	if ( '' === $path ) {
		$on = is_front_page();
	} else {
		$page = is_page() ? get_page_by_path( $path ) : null;
		$id   = get_queried_object_id();
		$on   = $page && ( $page->ID === $id || in_array( $page->ID, get_post_ancestors( $id ), true ) );
	}
	if ( $on ) {
		echo ' aria-current="page"';
	}
}

/** Meta description of the current page, from inc/pages.php. */
function utalk_current_description() {
	$path = null;
	if ( is_front_page() ) {
		$path = '';
	} elseif ( is_page() ) {
		$path = get_page_uri( get_queried_object_id() );
	}
	if ( null === $path ) {
		return '';
	}
	foreach ( utalk_pages() as $row ) {
		if ( $row[0] === $path ) {
			return $row[2];
		}
	}
	return '';
}

/* ---------------------------------------------------------------------------
 * Activation: create the pages, set the home page and pretty permalinks
 * ------------------------------------------------------------------------ */
add_action( 'after_switch_theme', 'utalk_setup_site' );

// Theme updates (Replace active with uploaded) don't fire after_switch_theme:
// create any page added in a newer version the first time an admin opens the dashboard.
add_action(
	'admin_init',
	function () {
		if ( get_option( 'utalk_pages_version' ) !== UTALK_VERSION && current_user_can( 'manage_options' ) ) {
			utalk_setup_site();
		}
	}
);

function utalk_setup_site() {
	$ids   = array();
	$order = 0;

	foreach ( utalk_pages() as $row ) {
		list( $path, $title ) = $row;
		$path = '' === $path ? 'accueil' : $path;
		$page = get_page_by_path( $path );

		if ( $page ) {
			$ids[ $path ] = $page->ID;
			continue;
		}

		$parent_path  = dirname( $path );
		$ids[ $path ] = wp_insert_post(
			array(
				'post_type'   => 'page',
				'post_status' => 'publish',
				'post_title'  => $title,
				'post_name'   => basename( $path ),
				'post_parent' => isset( $ids[ $parent_path ] ) ? $ids[ $parent_path ] : 0,
				'menu_order'  => $order++,
			)
		);
	}

	// A static home page (the design lives in front-page.php). Keep an existing static front page.
	if ( 'page' !== get_option( 'show_on_front' ) && ! empty( $ids['accueil'] ) ) {
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', $ids['accueil'] );
	}

	// Page URLs like /langues/english/ need pretty permalinks. Only switch from "Plain".
	if ( '' === get_option( 'permalink_structure' ) ) {
		update_option( 'permalink_structure', '/%postname%/' );
	}
	flush_rewrite_rules();
	update_option( 'utalk_pages_version', UTALK_VERSION );
}

/* ---------------------------------------------------------------------------
 * Contact form: saves every request under "Messages UTALK" and emails the admin
 * ------------------------------------------------------------------------ */
add_action(
	'init',
	function () {
		register_post_type(
			'utalk_message',
			array(
				'labels'          => array(
					'name'          => 'Messages UTALK',
					'singular_name' => 'Message',
					'menu_name'     => 'Messages UTALK',
					'all_items'     => 'Tous les messages',
					'edit_item'     => 'Message',
					'not_found'     => 'Aucun message pour l’instant.',
				),
				'public'          => false,
				'show_ui'         => true,
				'show_in_menu'    => true,
				'menu_position'   => 25,
				'menu_icon'       => 'dashicons-email-alt',
				'supports'        => array( 'title', 'editor' ),
				'capability_type' => 'post',
				'capabilities'    => array( 'create_posts' => 'do_not_allow' ),
				'map_meta_cap'    => true,
			)
		);
	}
);

function utalk_contact_hidden_fields() {
	echo '<input type="hidden" name="action" value="utalk_contact">';
	// Honeypot: humans never see or fill it.
	echo '<div class="hp" aria-hidden="true"><label>Site web <input type="text" name="website" value="" tabindex="-1" autocomplete="off"></label></div>';
}

/** Print " hidden" unless the page was reloaded with ?contact=$state. */
function utalk_contact_hidden( $state ) {
	$current = isset( $_GET['contact'] ) ? sanitize_key( wp_unslash( $_GET['contact'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	if ( $current !== $state ) {
		echo ' hidden';
	}
}

add_action( 'admin_post_nopriv_utalk_contact', 'utalk_handle_contact' );
add_action( 'admin_post_utalk_contact', 'utalk_handle_contact' );

function utalk_handle_contact() {
	// phpcs:disable WordPress.Security.NonceVerification.Missing -- public form, cached pages; spam is stopped by the honeypot.
	$back = wp_get_referer();
	$back = remove_query_arg( 'contact', $back ? $back : home_url( '/' ) );

	if ( ! empty( $_POST['website'] ) ) {
		wp_safe_redirect( add_query_arg( 'contact', 'sent', $back ) . '#contact' );
		exit;
	}

	$name  = isset( $_POST['nom'] ) ? sanitize_text_field( wp_unslash( $_POST['nom'] ) ) : '';
	$phone = isset( $_POST['telephone'] ) ? sanitize_text_field( wp_unslash( $_POST['telephone'] ) ) : '';
	$email = isset( $_POST['email'] ) ? sanitize_email( wp_unslash( $_POST['email'] ) ) : '';
	$lang  = isset( $_POST['langue'] ) ? sanitize_text_field( wp_unslash( $_POST['langue'] ) ) : '';
	// phpcs:enable

	if ( '' === $name || '' === $phone || ! is_email( $email ) || '' === $lang ) {
		wp_safe_redirect( add_query_arg( 'contact', 'error', $back ) . '#contact' );
		exit;
	}

	$body = "Nom : $name\nTéléphone : $phone\nEmail : $email\nLangue : $lang\nEnvoyé depuis : $back";

	wp_insert_post(
		array(
			'post_type'    => 'utalk_message',
			'post_status'  => 'private',
			'post_title'   => "$name · $lang",
			'post_content' => $body,
		)
	);

	$to = apply_filters( 'utalk_contact_to', get_option( 'admin_email' ) );
	wp_mail( $to, "[UTALK] Nouvelle demande : $name ($lang)", $body, array( "Reply-To: $name <$email>" ) );

	wp_safe_redirect( add_query_arg( 'contact', 'sent', $back ) . '#contact' );
	exit;
}

/* ---------------------------------------------------------------------------
 * WooCommerce
 * ------------------------------------------------------------------------ */
add_filter( 'woocommerce_show_page_title', '__return_false' ); // woocommerce.php prints the title in the page header.

/** Cart, checkout and account pages use the full container width. */
function utalk_is_wide_page() {
	return function_exists( 'is_cart' ) && ( is_cart() || is_checkout() || is_account_page() );
}
