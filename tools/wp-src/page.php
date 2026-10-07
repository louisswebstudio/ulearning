<?php
/**
 * Any page without its own template: legal pages, WooCommerce cart / checkout / account, new pages.
 *
 * @package utalk
 */

get_header();

while ( have_posts() ) :
	the_post();
	?>
<section class="course-hero">
  <div class="container">
    <h1 class="course-hero__title page-hero__title"><?php the_title(); ?></h1>
  </div>
</section>

<section class="wp-section">
  <div class="container">
    <div class="wp-content<?php echo utalk_is_wide_page() ? ' wp-content--wide' : ''; ?>">
      <?php the_content(); ?>
    </div>
  </div>
</section>
	<?php
endwhile;

get_footer();
