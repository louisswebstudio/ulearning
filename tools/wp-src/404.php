<?php
/**
 * Page not found.
 *
 * @package utalk
 */

get_header();
?>
<section class="course-hero">
  <div class="container">
    <h1 class="course-hero__title page-hero__title">Cette page n’existe pas</h1>
    <p class="page-hero__lead">Le lien est peut-être ancien. Choisissez une langue ou revenez à l’accueil.</p>
  </div>
</section>

<section class="wp-section">
  <div class="container wp-404">
    <a class="btn btn--primary" href="<?php echo esc_url( home_url( '/' ) ); ?>">Retour à l’accueil</a>
    <a class="btn btn--outline" href="<?php echo esc_url( utalk_url( 'langues' ) ); ?>">Voir les langues</a>
  </div>
</section>
<?php
get_footer();
