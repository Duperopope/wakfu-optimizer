/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.HashMap;

public class fwr
implements aqz {
    protected short avX;
    protected int emw;
    protected int[] emx;
    protected HashMap<Integer, int[]> emy;

    public short aIi() {
        return this.avX;
    }

    public int cpU() {
        return this.emw;
    }

    public int[] cpV() {
        return this.emx;
    }

    public HashMap<Integer, int[]> cpW() {
        return this.emy;
    }

    @Override
    public void reset() {
        this.avX = 0;
        this.emw = 0;
        this.emx = null;
        this.emy = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.avX = aqH2.bGG();
        this.emw = aqH2.bGI();
        this.emx = aqH2.bGM();
        int n = aqH2.bGI();
        this.emy = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            int n2 = aqH2.bGI();
            int[] nArray = aqH2.bGM();
            this.emy.put(n2, nArray);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oza.d();
    }
}
