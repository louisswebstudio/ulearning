<?php
/**
 * Fallback for posts, archives and search.
 *
 * @package utalk
 */

get_header();

if ( is_singular() ) {
	$heading = single_post_title( '', false );
} elseif ( is_home() ) {
	$heading = get_option( 'page_for_posts' ) ? get_the_title( get_option( 'page_for_posts' ) ) : 'Actualités';
} elseif ( is_search() ) {
	/* translators: %s: search query */
	$heading = sprintf( 'Résultats pour « %s »', get_search_query() );
} else {
	$heading = wp_strip_all_tags( get_the_archive_title() );
}
?>
<section class="course-hero">
  <div class="container">
    <h1 class="course-hero__title page-hero__title"><?php echo esc_html( $heading ); ?></h1>
  </div>
</section>

<section class="wp-section">
  <div class="container">
	<?php if ( is_singular() ) : ?>
		<?php
		while ( have_posts() ) :
			the_post();
			?>
		<article <?php post_class( 'wp-content' ); ?>>
			<?php if ( has_post_thumbnail() ) : ?>
				<figure class="wp-thumb"><?php the_post_thumbnail( 'large' ); ?></figure>
			<?php endif; ?>
			<?php the_content(); ?>
		</article>
		<?php endwhile; ?>
	<?php elseif ( have_posts() ) : ?>
	<ul class="wp-cards">
		<?php
		while ( have_posts() ) :
			the_post();
			?>
		<li <?php post_class( 'wp-card' ); ?>>
			<a href="<?php the_permalink(); ?>">
				<?php if ( has_post_thumbnail() ) : ?>
					<figure class="wp-card__media"><?php the_post_thumbnail( 'medium_large' ); ?></figure>
				<?php endif; ?>
				<p class="wp-card__date"><?php echo esc_html( get_the_date() ); ?></p>
				<h2 class="wp-card__title"><?php the_title(); ?></h2>
				<p class="wp-card__text"><?php echo esc_html( wp_trim_words( get_the_excerpt(), 24 ) ); ?></p>
			</a>
		</li>
		<?php endwhile; ?>
	</ul>
		<?php the_posts_pagination(); ?>
	<?php else : ?>
	<div class="wp-content">
		<p>Aucun contenu pour l’instant.</p>
		<p><a class="btn btn--primary" href="<?php echo esc_url( home_url( '/' ) ); ?>">Retour à l’accueil</a></p>
	</div>
	<?php endif; ?>
  </div>
</section>
<?php
get_footer();
