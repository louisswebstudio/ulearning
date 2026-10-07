<?php
/**
 * WooCommerce shop, product categories and single products.
 *
 * @package utalk
 */

get_header();

if ( ! is_singular( 'product' ) ) :
	?>
<section class="course-hero">
  <div class="container">
    <h1 class="course-hero__title page-hero__title"><?php woocommerce_page_title(); ?></h1>
  </div>
</section>
<?php endif; ?>

<section class="wp-section wc-section">
  <div class="container">
	<?php woocommerce_content(); ?>
  </div>
</section>
<?php
get_footer();
