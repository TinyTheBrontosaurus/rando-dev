from rando import draw_gpx


def test_rdp():
    draw_gpx.rdp_snapped(
        xs=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        ys=[0, 0.25, 0.25, 0.25, 0.25, 0, 0, 0, 0, -0.25, -0.25]
    )